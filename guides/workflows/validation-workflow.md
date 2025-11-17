# Validation and Troubleshooting Workflow

## Token Budget Tracker

**This Workflow**:
- Tier 1 (Metadata): 100 tokens ✅ (already loaded)
- Tier 2 (SKILL.md): 2,250 tokens ✅ (already loaded)
- This guide: ~1,000 tokens
- validate_config.py output: 0 tokens (script execution)
- **Estimated total**: 3,350 tokens
- **Status**: ✅ Within budget (<10,000)

---

## Purpose

Validate permission configuration and troubleshoot issues:
- "validate my permissions"
- "check for errors in settings"
- "why isn't git working?"
- "troubleshoot permission denied"

**When triggered**: User requests validation OR after complex permission changes

---

## Prerequisites

**This workflow triggered when**:
- User explicitly requests: "validate", "check", "troubleshoot"
- After major changes: profile application, multi-tool setup
- User reports permission errors: "not working", "denied"
- Proactive validation (after complex operations)

---

## Workflow Steps

### Step 1: Execute validate_config.py

**Command**:
```bash
python3 scripts/validate_config.py
```

**What validate_config.py checks**:
1. ✅ **Syntax validation**: All rules match `Tool(pattern)` format
2. ✅ **Tool name validation**: Tools are in VALID_TOOLS list
3. ✅ **Glob pattern validation**: Patterns are syntactically correct
4. ✅ **Conflict detection**: Allow vs deny overlaps
5. ✅ **Security audit**: Sensitive patterns not in allow rules
6. ✅ **Completeness check**: Essential operations covered

**Token Cost**: 0 tokens (script execution)

**Expected Output** (success):
```
✅ Validation Summary

Settings file: /path/to/settings.json
Last modified: 2025-01-16 15:45:12

Syntax Validation:
  ✅ All 45 allow rules are syntactically valid
  ✅ All 12 deny rules are syntactically valid

Tool Name Validation:
  ✅ All tools recognized: Bash, Read, Write, Edit, WebFetch

Glob Pattern Validation:
  ✅ All 23 file patterns are valid
  ✅ No malformed globs detected

Conflict Detection:
  ⚠️  1 potential conflict found:
      Allow: Bash(git push *)
      Deny: Bash(git push * --force)
      Resolution: Deny rule is more specific (OK)

Security Audit:
  ✅ No sensitive files in allow rules
  ✅ Dangerous commands properly denied
  ✅ Security score: 95/100

Completeness Check:
  ✅ Read access: Configured
  ✅ Edit access: Configured
  ✅ Command execution: Configured

Overall Status: ✅ VALID
```

**Expected Output** (errors found):
```
❌ Validation Summary

Settings file: /path/to/settings.json
Last modified: 2025-01-16 15:45:12

Syntax Validation:
  ❌ 2 syntax errors found:
      Line 45: "Bahs(git status *)" - Invalid tool name (did you mean "Bash"?)
      Line 78: "Edit(**/.md)" - Invalid glob (leading dot after **)

Tool Name Validation:
  ✅ All tools recognized

Glob Pattern Validation:
  ❌ 1 invalid pattern:
      "src/**.rs)" - Unmatched parenthesis

Conflict Detection:
  ⚠️  2 conflicts found:
      1. Allow: Write(**.env) vs Deny: Write(.env*) - SECURITY RISK
      2. Allow: Bash(rm *) vs Deny: Bash(rm *) - Contradiction

Security Audit:
  ❌ SECURITY ISSUES:
      - Write(.env*) found in allow rules (CRITICAL)
      - Bash(sudo *) not in deny rules (WARNING)
  ⚠️  Security score: 45/100

Overall Status: ❌ INVALID (3 errors, 2 warnings)
```

---

### Step 2: Analyze Validation Results

**Parse script output for**:
- Error count
- Warning count
- Specific issues (syntax, security, conflicts)
- Overall status (valid/invalid)

**Categorize issues**:

**CRITICAL** (must fix immediately):
- Syntax errors (settings.json won't load)
- Security vulnerabilities (.env in allow rules)
- Tool name errors

**WARNING** (should fix, not blocking):
- Conflicts (allow vs deny overlaps)
- Missing security denies
- Overly broad patterns

**INFO** (non-issues):
- Benign conflicts (deny is more specific than allow)
- Low security score but no actual vulns

**Token Cost**: 0 tokens (parsing script output)

---

### Step 3: Report Issues to User

**Format by severity**:

```markdown
## Validation Results

### ❌ Critical Issues (3)

**1. Syntax Error** (Line 45):
```
"Bahs(git status *)"
```
**Problem**: Invalid tool name "Bahs"
**Fix**: Change to `Bash(git status *)`

**2. Security Vulnerability** (Line 102):
```
"Write(.env*)"
```
**Problem**: Allows writing to .env files (contains secrets)
**Fix**: Remove from allow rules, ensure in deny rules

**3. Invalid Glob Pattern** (Line 78):
```
"Edit(**/.md)"
```
**Problem**: Leading dot after ** is invalid
**Fix**: Change to `Edit(**.md)`

---

### ⚠️ Warnings (2)

**1. Conflict Detected**:
- Allow: `Bash(rm *)`
- Deny: `Bash(rm *)`
**Problem**: Contradictory rules
**Recommendation**: Remove from allow rules (keep in deny for safety)

**2. Missing Security Deny**:
**Problem**: `Bash(sudo *)` not in deny rules
**Recommendation**: Add to deny rules to prevent privilege escalation

---

### ✅ Passed Checks
- All tool names valid (except 1 typo)
- Most glob patterns correct
- No credential files in allow rules (except .env issue)

---

**Security Score**: 45/100 (LOW - fix critical issues)
**Status**: ❌ Invalid (must fix before restart)
```

**Token Cost**: 0 tokens (output to user)

---

### Step 4: Offer Automatic Fixes

**For fixable issues, offer auto-repair**:

```markdown
## Automatic Fixes Available

I can automatically fix the following issues:

**Syntax Errors**:
1. ✅ "Bahs" → "Bash" (Line 45)
2. ✅ "**/.md" → "**.md" (Line 78)

**Security Issues**:
3. ✅ Remove "Write(.env*)" from allow rules
4. ✅ Add "Bash(sudo *)" to deny rules

**Conflicts**:
5. ✅ Remove "Bash(rm *)" from allow rules

**Apply all fixes automatically? (yes/no/select)**

Options:
- **yes**: Apply all 5 fixes
- **no**: I'll fix manually
- **select**: Choose which fixes to apply
```

**If user says "yes"**:
- Proceed to Step 5 (apply fixes)

**If user says "select"**:
- Ask which fixes to apply
- Proceed to Step 5 with selected fixes

**If user says "no"**:
- Skip to Step 6 (manual guidance)

**Token Cost**: 0 tokens (user interaction)

---

### Step 5: Apply Automatic Fixes

**For each approved fix**:

**Fix 1: Syntax error (Bahs → Bash)**:
```bash
python3 scripts/apply_permissions.py \
  --remove-allow "Bahs(git status *)" \
  --allow "Bash(git status *)"
```

**Fix 2: Invalid glob (** /.md → **.md)**:
```bash
python3 scripts/apply_permissions.py \
  --remove-allow "Edit(**/.md)" \
  --allow "Edit(**.md)"
```

**Fix 3: Security vuln (remove Write(.env*))**:
```bash
python3 scripts/apply_permissions.py \
  --remove-allow "Write(.env*)" \
  --deny "Write(.env*)"
```

**Fix 4: Missing deny (add sudo)**:
```bash
python3 scripts/apply_permissions.py \
  --deny "Bash(sudo *)"
```

**Fix 5: Conflict (remove rm from allow)**:
```bash
python3 scripts/apply_permissions.py \
  --remove-allow "Bash(rm *)"
```

**Script handles**:
- Backup before changes
- Validation after changes
- Rollback if new errors introduced

**Token Cost**: 0 tokens (script execution)

**Expected Output**:
```
✅ Backup created: settings.20250116_160235.backup
✅ Applied 5 fixes successfully
✅ Re-validation passed: 0 errors, 0 warnings
✅ Settings written to: settings.json

Summary:
  Fixed syntax errors: 2
  Fixed security issues: 2
  Resolved conflicts: 1
  New security score: 95/100 (HIGH)
```

---

### Step 6: Re-Validate After Fixes

**Run validate_config.py again**:

```bash
python3 scripts/validate_config.py
```

**Verify**:
- Previous errors are gone
- No new errors introduced
- Security score improved

**If validation now passes**:
```markdown
✅ **Validation passed after fixes**

All critical issues resolved:
- ✅ Syntax errors fixed (2)
- ✅ Security vulnerabilities patched (2)
- ✅ Conflicts resolved (1)

**New security score**: 95/100 (HIGH)
**Status**: ✅ VALID

**Next step**: Restart Claude Code for changes to take effect.
```

**If validation still fails**:
```markdown
❌ **Validation still failing**

Remaining issues:
- <List new/unfixed errors>

**Recommendation**:
1. Review settings.json manually
2. Or restore from backup: see backup-restore-workflow.md
3. Or contact support with error details
```

**Token Cost**: 0 tokens (script execution + output)

---

## Troubleshooting Specific Errors

### Troubleshooting 1: "Permission denied" errors

**User reports**: "I get permission denied when running git status"

**Diagnostic Steps**:

**Step A: Check if command is allowed**:
```bash
grep "Bash(git status" settings.json
```

**If NOT found**:
```markdown
❌ **Root cause**: git status not in allowed commands

**Fix**: Enable git read-only permissions
→ Run: "enable git read-only"
→ Or use cli-tool-workflow.md
```

**If FOUND** in allow rules:
```markdown
⚠️  **Command is allowed but still denied**

Possible causes:
1. Settings not reloaded (restart Claude Code)
2. Typo in pattern (check exact syntax)
3. Conflicting deny rule (check deny rules)

**Next steps**:
- Have you restarted Claude Code after adding permission?
- Run validation to check for conflicts
```

---

### Troubleshooting 2: "File cannot be edited" errors

**User reports**: "Can't edit src/main.rs"

**Diagnostic Steps**:

**Step A: Check file pattern permissions**:
```bash
grep "Edit(.*\.rs)" settings.json
grep "Edit(src/" settings.json
```

**If NO matching pattern**:
```markdown
❌ **Root cause**: .rs files not editable

**Fix**: Enable Rust file editing
→ Run: "make src/**.rs editable"
→ Or use file-pattern-workflow.md
```

**If pattern exists**:
```bash
grep "Deny.*main.rs" settings.json
```

**If deny rule found**:
```markdown
⚠️  **Conflict**: main.rs is explicitly denied

**Fix**: Remove deny rule or make it more specific
→ Run validation to see conflict details
```

---

### Troubleshooting 3: Overly restrictive permissions

**User reports**: "I can't do anything!"

**Diagnostic Steps**:

**Step A: Check active profile**:
```bash
python3 scripts/validate_config.py | grep "Profile"
```

**If profile is "read-only" or "production"**:
```markdown
⚠️  **Cause**: Restrictive profile active

Current profile: read-only
This profile BLOCKS all editing and writes.

**Fix options**:
1. Apply development profile: "apply development profile"
2. Switch to code-review profile: "apply code-review profile"
3. Restore previous permissions: see backup-restore-workflow.md
```

**If no restrictive profile**:
```markdown
**Unusual**: No restrictive profile but still limited

**Debug**:
1. Run: `python3 scripts/validate_config.py` (full output)
2. Check for excessive deny rules
3. Check if allowedTools is empty
```

---

### Troubleshooting 4: Security score is low

**User reports**: "Validation says security score is 45/100"

**Analysis**:

**Low score causes**:
- Missing deny rules for dangerous commands
- Sensitive files in allow rules
- No .env protection
- Overly broad patterns (** in write rules)

**Improvement steps**:

```markdown
## Security Score Improvement

**Current score**: 45/100 (LOW)
**Target**: 80+ (HIGH)

**Recommendations**:

1. ✅ **Add missing deny rules** (+20 points):
   ```
   Bash(rm *)
   Bash(sudo *)
   Bash(git push * --force)
   Write(.env*)
   ```

2. ✅ **Remove sensitive files from allow** (+15 points):
   - Remove: Write(.env*), Edit(*.key), Read(*.pem)

3. ✅ **Narrow overly broad patterns** (+10 points):
   - Change: Write(**) → Write(src/**), Write(tests/**)
   - Reason: Build artifacts shouldn't be writable

**Apply security improvements? (yes/no)**
```

**If user says yes**:
- Apply recommended security fixes
- Re-validate
- Report new security score

---

## Examples

### Example 1: User Requests Validation

**User Request**: "validate my permissions"

**Workflow Execution**:
1. Run `python3 scripts/validate_config.py`
2. Output shows: 1 syntax error, 1 security warning
3. Parse and categorize issues
4. Report to user:
   ```
   ❌ 1 critical issue: Typo "Bahs" → "Bash"
   ⚠️ 1 warning: Missing sudo deny rule
   ```
5. Offer automatic fixes
6. User says "yes"
7. Apply fixes via apply_permissions.py
8. Re-validate → All passed ✅
9. Confirm: "Validation passed. Security score 95/100."

**Total tokens**: 3,350 ✅

---

### Example 2: Troubleshooting Permission Denied

**User Request**: "git status says permission denied"

**Workflow Execution**:
1. Recognize troubleshooting request
2. Check if git status in allow rules:
   ```bash
   grep "Bash(git status" settings.json
   ```
3. **NOT FOUND**
4. Diagnose: "git status not enabled"
5. Offer fix: "Enable git read-only? (yes/no)"
6. User says "yes"
7. Route to cli-tool-workflow.md with tool=git, mode=READ
8. Apply git permissions
9. Confirm: "git status now enabled. Restart Claude Code."

**Total tokens**: 3,400 ✅ (includes partial cli-tool-workflow)

---

### Example 3: Post-Profile Application Validation

**User Request**: "apply development profile"

**Workflow Execution**:
1. profile-application-workflow applies 68 rules
2. **Proactively validate** after profile application
3. Run `python3 scripts/validate_config.py`
4. Output: All passed, security score 90/100
5. Report: "Development profile applied and validated successfully ✅"

**Total tokens**: 3,450 ✅ (validation included in profile workflow)

**Use case**: Proactive validation after major changes

---

## Error Handling

### Error 1: validate_config.py script not found

**Detection**: Script execution fails with "No such file or directory"

**Action**:
```markdown
❌ **Validation script missing**

Expected location: scripts/validate_config.py
Status: Not found

**Possible causes**:
1. Skill not fully installed
2. Script deleted/moved
3. Wrong working directory

**Workaround**: Manual validation
→ Check settings.json syntax with: `jq . settings.json`
→ Look for obvious errors
```

**Recovery**: Manual validation or reinstall skill

---

### Error 2: settings.json malformed (cannot parse)

**Detection**: validate_config.py crashes with JSON parse error

**Example Error**:
```
JSONDecodeError: Expecting ',' delimiter: line 45 column 5
```

**Action**:
```markdown
❌ **CRITICAL: settings.json is malformed**

Claude Code may not start with corrupted settings.

**Immediate action**:
1. Restore from most recent backup:
   → `cp settings.BACKUP settings.json`
2. Or see backup-restore-workflow.md

**After restore**:
- Review what changes caused corruption
- Re-apply changes carefully
```

**Recovery**: MUST restore from backup (corrupted settings breaks Claude Code)

---

### Error 3: Validation passes but permissions still don't work

**Detection**: validate_config.py says ✅ but user still gets permission denied

**Diagnostic**:
```markdown
⚠️  **Validation passed but permissions not working**

**Checklist**:
1. ✅ Validation passed
2. ❓ Have you restarted Claude Code? (REQUIRED)
3. ❓ Are you using the correct Claude Code workspace?
4. ❓ Is settings.json in the correct location?

**Debug steps**:
1. Restart Claude Code (most common fix)
2. Verify settings.json location: `~/.config/claude-code/settings.json`
3. Check if multiple settings.json files exist (config precedence)
4. Try manual test: Add a simple rule like `Read(**)` and test

**If still failing**: Report issue with validation output
```

**Most common cause**: User forgot to restart Claude Code

---

## Edge Cases

### Edge Case 1: Too many errors to auto-fix

**Example**: 50+ syntax errors from manual editing gone wrong

**Handling**:
```markdown
⚠️  **Too many errors to auto-fix (50+)**

**Recommendation**: Restore from backup instead

Backups available:
- settings.20250116_153020.backup (30 min ago) ✅ Recommended
- settings.20250116_120045.backup (3 hours ago)
- settings.20250115_180512.backup (yesterday)

**Restore most recent backup? (yes/no)**

Or: Fix manually in text editor
```

**Policy**: If >20 errors, suggest backup restore instead of fixes

---

### Edge Case 2: Security score low but no specific errors

**Example**: Score 50/100 but validation shows no critical issues

**Cause**: Missing recommended deny rules (not required, but good practice)

**Handling**:
```markdown
⚠️  **Security score low (50/100) but no critical errors**

**Reason**: Missing recommended deny patterns

**Recommended additions** (optional but advised):
- Bash(rm -rf *)
- Bash(chmod 777 *)
- Bash(chown *)
- Write(~/.ssh/**)
- Write(~/.aws/**)

These are best practices but not strictly required.

**Add recommended denies for 95/100 score? (yes/no)**
```

**User choice**: Can proceed with 50/100 or improve to 95/100

---

### Edge Case 3: Validation differs from runtime behavior

**Example**: Validation says Bash(git status *) allowed but still permission denied at runtime

**Possible causes**:
1. Syntax slightly different in actual command vs pattern
2. Settings not reloaded
3. Different settings.json being used
4. Hook blocking the command

**Diagnosis**:
```markdown
**Pattern in settings**: `Bash(git status *)`
**Command you're running**: `git status -sb`

**Match**: ✅ Should work

**Troubleshooting**:
1. Restart Claude Code (reload settings)
2. Check for hooks blocking commands (see CLAUDE.md)
3. Verify settings.json location: `~/.config/claude-code/settings.json`
4. Try simpler command: `git status` (no flags)

If still failing: Settings may not be loading (check logs)
```

---

## Success Criteria

**Workflow complete when**:
- ✅ validate_config.py executed successfully
- ✅ Results parsed and categorized (critical/warning/info)
- ✅ Issues reported to user clearly
- ✅ Fixes offered (automatic or manual guidance)
- ✅ (If fixes applied) Re-validation passed
- ✅ User informed of final validation status
- ✅ Restart reminder provided (if changes made)

---

## Token Budget Summary

**Simple validation (no errors)**:
```
Tier 1 (Metadata):          100 tokens ✅
Tier 2 (SKILL.md):        2,250 tokens ✅
validation-workflow.md:   1,000 tokens (this file)
validate_config.py:           0 tokens (script execution)
---
Total:                    3,350 tokens
Status:                   ✅ 66% under budget
```

**Validation with fixes**:
```
Tier 1 + 2 + this:        3,350 tokens ✅
apply_permissions.py:         0 tokens (script execution)
Re-validation:                0 tokens (script execution)
---
Total:                    3,350 tokens
Status:                   ✅ 66% under budget
```

**Troubleshooting + routing to fix workflow**:
```
Tier 1 + 2 + this:        3,350 tokens ✅
Diagnostic checks:            0 tokens (script/grep execution)
Route to cli-tool:        1,500 tokens (load workflow)
---
Total:                    4,850 tokens
Status:                   ✅ 51% under budget
```

---

## Integration with Other Workflows

**Validation is used BY**:
- profile-application-workflow (post-profile validation)
- cli-tool-workflow (post-addition validation)
- project-setup-workflow (post-template validation)

**Validation routes TO**:
- backup-restore-workflow (if too many errors → restore)
- cli-tool-workflow (if missing tool permissions)
- file-pattern-workflow (if missing file permissions)

**Validation is**: A supporting workflow called by others + standalone

---

## Next Steps After Workflow

**If validation passed**:
- ✅ Settings are correct
- ✅ Safe to continue using
- ✅ Restart Claude Code if changes were made

**If validation failed and fixed**:
- ✅ Issues resolved
- ✅ Re-validation passed
- ✅ Restart Claude Code required

**If validation failed and NOT fixed**:
- ❌ Review errors manually
- ❌ Restore from backup if needed
- ❌ Don't restart Claude Code (may not load)

---

**End of Validation Workflow**
**Size**: ~500 lines (~2,500 tokens)
**Compliance**: ✅ Tier 3 (loaded on-demand only)
