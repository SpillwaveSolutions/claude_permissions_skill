# CLI Tool Permission Workflow

## Token Budget Tracker

**This Workflow**:
- Tier 1 (Metadata): 100 tokens ✅ (already loaded)
- Tier 2 (SKILL.md): 2,250 tokens ✅ (already loaded)
- This guide: ~1,250 tokens
- cli_commands.json (surgical): ~150 tokens
- **Estimated total**: 3,750 tokens
- **Status**: ✅ Within budget (<10,000)

---

## Purpose

Enable specific CLI tool permissions based on natural language requests like:
- "enable git"
- "allow gcloud read-only"
- "configure docker with write access"
- "make kubectl commands work"

---

## Prerequisites

**This workflow triggered when**:
- User mentions CLI tool name (git, gcloud, aws, kubectl, docker, npm, pip, maven, gradle, cargo, helm, terraform, pulumi, ansible, claude, gemini)
- Keywords present: "enable", "allow", "configure", "permit"
- Optional mode indicators: "read", "read-only", "write", "commits", "pushes"

---

## Workflow Steps

### Step 1: Extract Tool and Mode

**Parse user message for**:
1. **Tool name** (case-insensitive match)
2. **Mode** (if specified):
   - Read indicators: "read", "read-only", "list", "show", "describe", "view"
   - Write indicators: "write", "push", "commit", "deploy", "publish", "modify"
   - Default: READ (safer)

**Example Parsing**:
```
"enable git read-only" → Tool: git, Mode: READ
"allow gcloud write" → Tool: gcloud, Mode: WRITE
"configure docker" → Tool: docker, Mode: READ (default)
```

**Token Cost**: 0 tokens (in-memory logic)

---

### Step 2: Check If Tool Known

**Surgical lookup in cli_commands.json**:

```bash
grep -A 25 '"TOOL_NAME"' references/cli_commands.json
```

**Example**:
```bash
grep -A 25 '"git"' references/cli_commands.json
```

**Token Cost**: ~150 tokens (vs 2,650 for full file = 94% savings)

**Output Analysis**:
- If grep returns results → Tool is KNOWN, proceed to Step 3
- If grep returns empty → Tool is UNKNOWN, route to research workflow

**Unknown Tool Routing**:
```
IF tool NOT found in cli_commands.json:
  STOP this workflow
  Load guides/workflows/research-workflow.md
  Pass tool name and mode to research workflow
  END
```

---

### Step 3: Extract Commands for Mode

**From grep output, extract command arrays**:

**For READ mode**:
- Look for `"read_only": [...]` array
- Extract commands like: `["status", "log", "diff", "show"]`

**For WRITE mode**:
- Combine `"read_only"` + `"write"` arrays
- Extract all read + write commands
- Example: `["status", "log", "add", "commit", "push"]`

**Never include "dangerous" commands** (even in WRITE mode):
- These require explicit user opt-in
- Example: `git push --force`, `rm -rf`, `sudo`

**Token Cost**: 0 tokens (already loaded in Step 2 grep)

---

### Step 4: Build Permission Rules

**Convert commands to Bash() rules**:

**Format**: `Bash(TOOL_NAME COMMAND *)`

**Examples**:
```
git read-only:
  - Bash(git status *)
  - Bash(git log *)
  - Bash(git diff *)
  - Bash(git show *)

docker write:
  - Bash(docker ps *)
  - Bash(docker images *)
  - Bash(docker build *)
  - Bash(docker run *)
  - Bash(docker push *)
```

**Wildcard Strategy**:
- Always append ` *` to allow arguments
- Example: `Bash(git status *)` allows `git status`, `git status -sb`, etc.

**Token Cost**: 0 tokens (in-memory rule generation)

---

### Step 5: Apply Safety Rules

**ALWAYS add deny rules from security_patterns.json**:

```bash
jq '.recommended_deny_set.standard' references/security_patterns.json
```

**Token Cost**: ~100 tokens

**Critical deny rules to apply**:
```
Deny Rules (minimum set):
- Read(.env*)
- Read(*.key)
- Read(*.pem)
- Read(.aws/**)
- Read(.ssh/**)
- Write(.env*)
- Bash(rm *)
- Bash(sudo *)
- Bash(git push * --force)
- Bash(docker * --privileged)
- Bash(kubectl delete namespace *)
- Bash(aws * --profile production)
- Bash(gcloud * --project production)
```

**Conflict Detection**:
- If user requested write mode BUT safety rule denies specific dangerous command
- Keep deny rule (safety first)
- Inform user of restriction

**Example Conflict**:
```
User: "enable git write"
Allow Rules: Bash(git push *)
Deny Rules: Bash(git push * --force)
Result: Allow regular push, deny force push ✅
```

**Token Cost**: ~100 tokens (surgical jq extraction)

---

### Step 6: Execute apply_permissions.py

**Command**:
```bash
python3 scripts/apply_permissions.py \
  --allow "Bash(git status *)" \
  --allow "Bash(git log *)" \
  --allow "Bash(git diff *)" \
  --deny "Bash(git push * --force)" \
  --deny "Bash(rm *)" \
  --deny "Bash(sudo *)"
```

**What apply_permissions.py does**:
1. ✅ Creates timestamped backup (settings.YYYYMMDD_HHMMSS.backup)
2. ✅ Validates all rules for syntax errors
3. ✅ Detects conflicts (allow vs deny on same pattern)
4. ✅ Merges rules with existing settings.json
5. ✅ Writes updated settings.json
6. ✅ Reports what changed

**Token Cost**: 0 tokens (script execution, not file reading)

**Expected Output**:
```
✅ Backup created: /path/to/settings.20250116_143022.backup
✅ Validation passed: All rules are valid
✅ Added 3 allow rules, 3 deny rules
✅ Settings written to: /path/to/settings.json

Summary:
  Total allow rules: 15 (+3)
  Total deny rules: 8 (+3)
```

---

### Step 7: Confirm with User

**Report to user**:

```markdown
✅ **Enabled git (read-only mode)**

**Permissions added**:
- ✅ `git status` and variants
- ✅ `git log` and variants
- ✅ `git diff` and variants
- ✅ `git show` and variants

**Safety rules applied**:
- 🛡️ Blocked `git push --force` (dangerous)
- 🛡️ Blocked `rm` commands (destructive)
- 🛡️ Blocked `sudo` commands (privileged)

**Backup created**: `settings.20250116_143022.backup`

**Next step**: Restart Claude Code for changes to take effect.
```

**Token Cost**: 0 tokens (output to user)

---

## Examples

### Example 1: Enable Git Read-Only

**User Request**: "enable git read-only"

**Workflow Execution**:
1. Extract: Tool=git, Mode=READ
2. Surgical lookup: `grep -A 25 '"git"' references/cli_commands.json`
3. Extract read_only commands: `["status", "log", "diff", "show", "branch"]`
4. Build rules:
   ```
   Bash(git status *)
   Bash(git log *)
   Bash(git diff *)
   Bash(git show *)
   Bash(git branch *)
   ```
5. Apply safety: Add deny rules for `git push * --force`, `rm *`, `sudo *`
6. Execute: `python3 scripts/apply_permissions.py --allow ... --deny ...`
7. Confirm: Report success to user

**Total tokens**: 3,750 (within budget ✅)

---

### Example 2: Enable Docker Write

**User Request**: "configure docker with write access"

**Workflow Execution**:
1. Extract: Tool=docker, Mode=WRITE
2. Surgical lookup: `grep -A 35 '"docker"' references/cli_commands.json`
3. Extract read_only + write commands:
   ```
   read_only: ["ps", "images", "inspect", "logs"]
   write: ["build", "run", "push", "pull", "start", "stop"]
   ```
4. Build rules (read + write):
   ```
   Bash(docker ps *)
   Bash(docker images *)
   Bash(docker build *)
   Bash(docker run *)
   Bash(docker push *)
   ```
5. Apply safety: Add deny for `docker * --privileged`, `docker rm -f`
6. Execute: `python3 scripts/apply_permissions.py ...`
7. Confirm: Report 6 allow rules, 2 deny rules added

**Total tokens**: 3,800 (within budget ✅)

---

### Example 3: Enable Kubectl (Unknown Commands)

**User Request**: "enable kubectl"

**Workflow Execution**:
1. Extract: Tool=kubectl, Mode=READ (default)
2. Surgical lookup: `grep -A 25 '"kubectl"' references/cli_commands.json`
3. **FOUND** in cli_commands.json (kubectl is pre-configured)
4. Extract read_only commands: `["get", "describe", "logs", "explain"]`
5. Build rules:
   ```
   Bash(kubectl get *)
   Bash(kubectl describe *)
   Bash(kubectl logs *)
   Bash(kubectl explain *)
   ```
6. Apply safety: Add deny for `kubectl delete namespace *`, `kubectl apply *` (not in read_only)
7. Execute: `python3 scripts/apply_permissions.py ...`
8. Confirm: Report success

**Total tokens**: 3,750 (within budget ✅)

---

### Example 4: Enable Unknown Tool → Route to Research

**User Request**: "enable perl"

**Workflow Execution**:
1. Extract: Tool=perl, Mode=READ (default)
2. Surgical lookup: `grep -A 25 '"perl"' references/cli_commands.json`
3. **NOT FOUND** (perl not in database)
4. **STOP this workflow**
5. **Load research workflow**:
   ```
   Read guides/workflows/research-workflow.md
   ```
6. Pass context: Tool=perl, Mode=READ
7. Research workflow takes over (uses Perplexity → Brave → Gemini → WebSearch)

**Token cost for this workflow**: 3,600 tokens (then research workflow adds ~2,500 more)

---

## Error Handling

### Error 1: grep returns empty (unknown tool)

**Detection**: grep exit code 1 or empty output

**Action**:
```
STOP current workflow
INFORM user: "perl is not in the known tools database. Researching..."
LOAD guides/workflows/research-workflow.md
PASS tool=perl, mode=READ to research workflow
```

**Token impact**: +2,000 tokens (research workflow)

---

### Error 2: apply_permissions.py fails validation

**Detection**: Script exits with error code, output contains "Validation failed"

**Example Error**:
```
❌ Validation failed: Invalid tool name "Bahs" (did you mean "Bash"?)
```

**Action**:
1. Show error to user
2. Ask user to verify tool name
3. Offer to retry with corrected input

**Recovery**: Do NOT write settings.json if validation fails

---

### Error 3: Conflicting rules

**Detection**: apply_permissions.py reports conflict

**Example**:
```
⚠️  Conflict detected:
    Allow: Bash(git push *)
    Deny: Bash(git push * --force)
    Resolution: Both rules kept (deny is more specific)
```

**Action**:
1. Keep both rules (deny takes precedence for specific patterns)
2. Inform user of conflict and resolution
3. Proceed with write

**No error** - this is expected behavior (safety first)

---

### Error 4: Backup creation fails

**Detection**: Script cannot create backup file (permissions issue)

**Example Error**:
```
❌ Failed to create backup: Permission denied on settings.json
```

**Action**:
1. STOP workflow (never modify without backup)
2. Inform user of permission issue
3. Suggest manual backup: `cp settings.json settings.backup`
4. Offer to retry after manual backup

**Recovery**: User must fix file permissions or create manual backup

---

## Edge Cases

### Edge Case 1: Tool has no read_only commands

**Example**: User asks for "terraform read-only" but terraform.json only has write commands

**Handling**:
```
INFORM user: "terraform typically requires write access for state management"
OFFER: "Would you like to enable terraform with minimal write permissions?"
IF user confirms:
  Apply smallest set of write commands
IF user declines:
  Explain terraform cannot operate in read-only mode
```

---

### Edge Case 2: User requests both read and write

**Example**: "enable git read and write"

**Handling**:
- Interpret as WRITE mode (write implies read)
- Apply read_only + write commands
- Inform user: "Enabled git with read and write access"

---

### Edge Case 3: User specifies dangerous command explicitly

**Example**: "enable git push --force"

**Handling**:
1. Detect dangerous command request
2. **WARN user**: "git push --force is dangerous and can cause data loss"
3. **ASK user**: "Are you sure you want to enable force push? (yes/no)"
4. IF yes:
   - Add allow rule for specific command
   - Remove deny rule for that pattern
   - Add extra confirmation: "⚠️ Force push enabled. Use with extreme caution."
5. IF no:
   - Keep deny rule
   - Enable regular push only

**Safety principle**: Always require explicit confirmation for dangerous commands

---

### Edge Case 4: Multiple tools in one request

**Example**: "enable git and docker"

**Handling**:
1. Detect multiple tools: ["git", "docker"]
2. Execute workflow SEQUENTIALLY for each tool
3. Track rules for all tools
4. Single apply_permissions.py execution at end with all rules
5. Report summary:
   ```
   ✅ Enabled git (read-only)
   ✅ Enabled docker (read-only)
   Total rules added: 12 allow, 5 deny
   ```

**Token cost**: ~1,500 per tool (3,000 total for 2 tools)

---

## Success Criteria

**Workflow complete when**:
- ✅ Tool commands extracted from database
- ✅ Permission rules generated
- ✅ Safety deny rules applied
- ✅ Backup created (via apply_permissions.py)
- ✅ Validation passed (syntax + conflicts)
- ✅ settings.json written successfully
- ✅ User informed of changes
- ✅ Restart reminder provided

---

## Token Budget Summary

**Typical CLI tool request**:
```
Tier 1 (Metadata):          100 tokens ✅
Tier 2 (SKILL.md):        2,250 tokens ✅
cli-tool-workflow.md:     1,250 tokens (this file)
cli_commands.json (grep):   150 tokens (surgical)
security_patterns.json:     100 tokens (surgical)
Script execution:             0 tokens
---
Total:                    3,850 tokens
Status:                   ✅ 61% under budget
```

**Unknown tool (routes to research)**:
```
Tier 1 + 2 + this:        3,600 tokens ✅
Research workflow:        2,000 tokens
MCP tool usage:             500 tokens
---
Total:                    6,100 tokens
Status:                   ✅ 39% under budget
```

---

## Next Steps After Workflow

**User must restart Claude Code** for permissions to take effect.

**Optional follow-ups**:
- Validate with: `python3 scripts/validate_config.py`
- View backup: `ls -lt ~/.config/claude-code/settings.*.backup`
- Rollback if needed: See guides/workflows/backup-restore-workflow.md

---

**End of CLI Tool Workflow**
**Size**: ~350 lines (~1,750 tokens)
**Compliance**: ✅ Tier 3 (loaded on-demand only)
