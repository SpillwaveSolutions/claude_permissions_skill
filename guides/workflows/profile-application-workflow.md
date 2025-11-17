# Profile Application Workflow

## Token Budget Tracker

**This Workflow**:
- Tier 1 (Metadata): 100 tokens ✅ (already loaded)
- Tier 2 (SKILL.md): 2,250 tokens ✅ (already loaded)
- This guide: ~800 tokens
- permission_profiles.json (surgical): ~200 tokens
- **Estimated total**: 3,350 tokens
- **Status**: ✅ Within budget (<10,000)

---

## Purpose

Apply pre-built permission profiles for common workflows:
- "apply development profile"
- "use read-only profile"
- "configure for ci-cd"
- "switch to production profile"

**Key benefit**: Bulk permission changes (50-100+ rules) in one command

---

## Available Profiles

**From permission_profiles.json**:

| Profile | Use Case | Rules Count | Safety Level |
|---------|----------|-------------|--------------|
| **read-only** | Code review, security audit | ~30 | Maximum |
| **development** | Active coding (most common) | ~80 | High |
| **ci-cd** | Continuous integration | ~60 | High |
| **production** | Monitoring, read-only ops | ~25 | Maximum |
| **documentation** | Docs writing only | ~35 | High |
| **code-review** | PR review workflow | ~40 | High |
| **testing** | TDD workflow, test writing | ~70 | High |

---

## Prerequisites

**This workflow triggered when**:
- User mentions "profile": "apply X profile", "use Y profile", "switch to Z"
- Profile names: read-only, development, ci-cd, production, documentation, code-review, testing
- User wants bulk permission changes vs individual rules

---

## Workflow Steps

### Step 1: Identify Profile

**Parse user message for profile name**:

```
"apply development profile" → Profile: development
"use read-only" → Profile: read-only
"configure for ci-cd" → Profile: ci-cd
"switch to production profile" → Profile: production
```

**Case-insensitive matching**:
- "Development", "DEVELOPMENT", "development" → all match

**Aliases** (handle variations):
```
"dev" → development
"readonly" → read-only
"ci" / "ci/cd" / "cicd" → ci-cd
"prod" → production
"docs" → documentation
"review" → code-review
"test" → testing
```

**Token Cost**: 0 tokens (in-memory matching)

---

### Step 2: Load Profile Definition

**Surgical extraction from permission_profiles.json**:

```bash
jq '.PROFILE_NAME' assets/permission_profiles.json
```

**Examples**:

**For development profile**:
```bash
jq '.development' assets/permission_profiles.json
```

**For read-only profile**:
```bash
jq '."read-only"' assets/permission_profiles.json
```

**Token Cost**: ~200 tokens (vs 1,240 for full file = 84% savings)

---

### Step 3: Extract Profile Rules

**Profile Structure**:

```json
{
  "development": {
    "description": "Full development permissions for active coding",
    "use_cases": ["Active development", "Feature work", "Bug fixing"],
    "allow": [
      "Edit(**/*.{rs,py,js,ts,java,go,rb,php,cs,cpp,swift})",
      "Edit(**.md)",
      "Edit(**.json)",
      "Edit(**.yaml)",
      "Edit(**.toml)",
      "Write(src/**)",
      "Write(tests/**)",
      "Write(docs/**)",
      "Read(**)",
      "Bash(git status *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git diff *)",
      "Bash(cargo *)",
      "Bash(npm *)",
      "Bash(python3 *)",
      "Bash(mvn *)",
      "Bash(gradle *)"
    ],
    "deny": [
      "Write(.env*)",
      "Write(*.key)",
      "Write(*.pem)",
      "Edit(.env*)",
      "Read(.env*)",
      "Bash(rm *)",
      "Bash(sudo *)",
      "Bash(git push * --force)",
      "Bash(npm publish *)",
      "Bash(cargo publish *)"
    ]
  }
}
```

**Rule Count**:
- Allow rules: ~50-80 per profile
- Deny rules: ~10-20 per profile
- Total: ~60-100 rules

**Token Cost**: 0 tokens (already loaded in Step 2 jq output)

---

### Step 4: Confirm with User (Optional)

**For potentially destructive profiles**, confirm before applying:

**Profiles requiring confirmation**:
- **read-only**: Removes write access (may block work)
- **production**: Very restrictive (monitoring only)

**Confirmation prompt** (for read-only):
```markdown
⚠️  **Read-Only Profile**

This profile will:
- ✅ Enable reading all files
- ✅ Enable read-only git commands (status, log, diff)
- ❌ DISABLE file editing (Edit, Write)
- ❌ DISABLE git commits and pushes
- ❌ DISABLE build commands

**Use case**: Code review, security audit, or read-only exploration

**Apply read-only profile? (yes/no)**
```

**Profiles NOT requiring confirmation**:
- development (standard, expected)
- documentation (specific, limited)
- code-review (clear intent)
- testing (clear intent)

**Token Cost**: 0 tokens (user interaction)

---

### Step 5: Execute apply_permissions.py

**Command Construction** (example for development profile):

```bash
python3 scripts/apply_permissions.py \
  --allow "Edit(**/*.{rs,py,js,ts,java,go,rb,php,cs,cpp,swift})" \
  --allow "Edit(**.md)" \
  --allow "Edit(**.json)" \
  --allow "Write(src/**)" \
  --allow "Bash(git status *)" \
  --allow "Bash(git add *)" \
  --allow "Bash(cargo *)" \
  ... (50 more allow rules) \
  --deny "Write(.env*)" \
  --deny "Bash(rm *)" \
  --deny "Bash(sudo *)" \
  ... (10 more deny rules)
```

**Script Actions** (automatic):
1. ✅ Create timestamped backup
2. ✅ Validate all 60-100 rules
3. ✅ **REPLACE mode**: Clear existing allowedTools, apply profile from scratch
   - This ensures clean slate (no stale permissions)
4. ✅ Write updated settings.json
5. ✅ Report comprehensive summary

**Token Cost**: 0 tokens (script execution)

**Expected Output**:
```
✅ Backup created: settings.20250116_153512.backup
✅ Validation passed: All 78 rules are valid
✅ Applied development profile: 68 allow, 10 deny rules
✅ Settings written successfully (replaced previous permissions)

Summary:
  Total allow rules: 68 (replaced)
  Total deny rules: 10 (replaced)
  Profile: development
```

---

### Step 6: Confirm with User

**Report Format** (example for development profile):

```markdown
✅ **Development profile applied**

**File editing enabled**:
- ✅ All source code files (Rust, Python, JS, TS, Java, Go, Ruby, PHP, C#, C++, Swift)
- ✅ Markdown documentation (**.md)
- ✅ Configuration files (**.json, **.yaml, **.toml)
- ✅ Source directories (src/**, tests/**, docs/**)

**Commands enabled**:
- ✅ Git: status, add, commit, diff, log, branch
- ✅ Build tools: cargo, npm, python3, mvn, gradle
- ✅ Common utilities: ls, cat, grep, find

**Protected patterns**:
- 🛡️ .env*, *.key, *.pem (sensitive files)
- 🛡️ rm, sudo (dangerous commands)
- 🛡️ git push --force, npm/cargo publish (destructive operations)

**Total rules**: 68 allow, 10 deny

**Previous permissions**: Backed up to settings.20250116_153512.backup

**Next step**: Restart Claude Code for changes to take effect.
```

**Token Cost**: 0 tokens (output to user)

---

## Examples

### Example 1: Apply Development Profile

**User Request**: "apply development profile"

**Workflow Execution**:
1. Identify: Profile = development
2. Load: `jq '.development' assets/permission_profiles.json`
3. Extract: 68 allow rules + 10 deny rules
4. No confirmation needed (standard profile)
5. Execute: `python3 scripts/apply_permissions.py` in REPLACE mode
6. Confirm: Report 68 allow, 10 deny rules applied

**Total tokens**: 3,350 ✅

**Use case**: Starting active development on a project

---

### Example 2: Switch to Read-Only

**User Request**: "use read-only profile"

**Workflow Execution**:
1. Identify: Profile = read-only
2. Load: `jq '."read-only"' assets/permission_profiles.json`
3. Extract: 30 allow rules (all Read + git read-only) + 15 deny rules
4. **CONFIRM**: Ask user if they want to disable editing
5. User confirms: "yes"
6. Execute: `python3 scripts/apply_permissions.py` in REPLACE mode
7. Confirm: Report read-only mode active, editing disabled

**Total tokens**: 3,400 ✅

**Use case**: Security audit, code review without editing

---

### Example 3: Configure for CI/CD

**User Request**: "configure for ci-cd"

**Workflow Execution**:
1. Identify: Profile = ci-cd (matched from "ci-cd" or "ci/cd")
2. Load: `jq '."ci-cd"' assets/permission_profiles.json`
3. Extract rules:
   - Allow: Read all, build commands (cargo, npm, mvn), test commands, git (no push)
   - Deny: git push, publish commands, file editing (CI shouldn't edit source)
4. No confirmation needed
5. Execute: Apply ci-cd profile
6. Confirm: Report CI/CD permissions (build+test, no editing)

**Total tokens**: 3,350 ✅

**Use case**: Running in CI environment (GitHub Actions, GitLab CI)

---

### Example 4: Documentation Writing

**User Request**: "apply documentation profile"

**Workflow Execution**:
1. Identify: Profile = documentation (or "docs")
2. Load: `jq '.documentation' assets/permission_profiles.json`
3. Extract rules:
   - Allow: Edit(**.md), Edit(docs/**), Read(**), git status/add/commit
   - Deny: Edit source code (**.rs, **.py, etc.), build commands
4. No confirmation needed
5. Execute: Apply documentation profile
6. Confirm: Report docs-only permissions

**Total tokens**: 3,350 ✅

**Use case**: Technical writer working only on documentation

---

### Example 5: Testing/TDD Workflow

**User Request**: "switch to testing profile"

**Workflow Execution**:
1. Identify: Profile = testing (or "test")
2. Load: `jq '.testing' assets/permission_profiles.json`
3. Extract rules:
   - Allow: Edit test files (**.test.*, test_**, tests/**), Read source, test commands (pytest, jest, cargo test)
   - Allow: Read source code (for understanding), but no editing
   - Deny: Edit production source code
4. No confirmation needed
5. Execute: Apply testing profile
6. Confirm: Report TDD permissions (write tests, read source, run tests)

**Total tokens**: 3,400 ✅

**Use case**: Test-driven development, QA engineer workflow

---

## Error Handling

### Error 1: Unknown profile name

**Detection**: Profile not in permission_profiles.json

**Example**: "apply super-dev profile"

**Action**:
1. Inform: "Profile 'super-dev' not found"
2. List available: "Available profiles: read-only, development, ci-cd, production, documentation, code-review, testing"
3. Suggest: "Did you mean 'development'?"
4. Wait for clarification

**Recovery**: User selects valid profile

---

### Error 2: Confirmation declined

**Detection**: User says "no" to read-only confirmation

**Example**:
```
Prompt: "Apply read-only profile? (yes/no)"
User: "no"
```

**Action**:
1. Cancel profile application
2. Inform: "Read-only profile NOT applied. Permissions unchanged."
3. Offer: "Would you like a different profile? (development, code-review, testing)"

**Recovery**: User selects alternative profile or exits

---

### Error 3: Profile validation fails

**Detection**: apply_permissions.py validation error on profile rules

**Example Error**:
```
❌ Validation failed: Invalid glob pattern "**/{}" in profile
```

**Action**:
1. **CRITICAL**: This indicates profile database corruption
2. Report: "Profile database error. Please file issue at GitHub."
3. Offer: "Restore previous permissions from backup?"
4. If yes: Run backup-restore-workflow

**Recovery**: Restore from backup or manual fix

---

### Error 4: Backup creation fails

**Detection**: Cannot create backup before REPLACE

**Example Error**:
```
❌ Failed to create backup: Permission denied on settings.json
```

**Action**:
1. **STOP** workflow (NEVER replace without backup)
2. Inform: "Cannot apply profile without backup"
3. Suggest: "Fix file permissions or create manual backup: `cp settings.json settings.backup`"
4. Wait for user to resolve

**Recovery**: User fixes permissions, retry

---

## Edge Cases

### Edge Case 1: Switching between profiles

**Example**: Currently using read-only, switching to development

**Handling**:
1. Detect: Existing profile in settings.json (from metadata or comments)
2. Inform: "Switching from read-only → development"
3. Backup current (read-only settings)
4. **REPLACE** entirely with development profile
5. Report: "Switched from read-only to development. Previous settings backed up."

**REPLACE mode ensures clean transition** (no stale rules)

---

### Edge Case 2: Profile + custom rules

**Example**: User previously added custom rules, now applying profile

**Handling**:

**Option A: REPLACE mode (default)**:
- Wipe all previous permissions
- Apply profile from scratch
- **User loses custom rules**
- Backup preserves custom rules (can be restored)

**Option B: MERGE mode** (if user requests):
```
User: "apply development profile but keep my custom git rules"
```

**Action**:
1. Load profile
2. Detect custom rules in existing settings
3. **ASK**: "Found custom rules. Replace all or merge? (replace/merge)"
4. If merge:
   - Apply profile
   - Preserve custom rules that don't conflict
   - Inform: "Merged development profile with your custom rules"

**Default**: REPLACE (clean slate)

---

### Edge Case 3: Profile doesn't fit project type

**Example**: Using ci-cd profile but project needs specific build tool

**Workflow**:
1. Apply ci-cd profile (generic build commands)
2. User reports: "cargo test doesn't work"
3. **Diagnose**: ci-cd profile has generic commands, missing cargo-specific
4. **Suggest**: "Apply development profile OR run: 'enable cargo' to add cargo commands"

**Solution**: Profile + incremental CLI tool additions

---

### Edge Case 4: Production profile too restrictive

**Example**: User applies production, then can't do anything

**Workflow**:
1. User: "apply production profile"
2. Confirm: "Production is read-only. Continue?"
3. User: "yes" (mistakenly)
4. Applied: Very restrictive permissions
5. User reports: "I can't edit files now"
6. **Solution**: "Restore from backup or apply development profile"

**Prevention**: Clear confirmation messages for restrictive profiles

---

## Profile Descriptions Reference

### read-only Profile
**Purpose**: Code review, security audit, exploration
**Allow**: Read all files, git read-only (status, log, diff, show)
**Deny**: All editing, all writes, all git commits/pushes, all build commands
**Rules**: ~30 allow, ~15 deny
**Safety**: Maximum (no modifications possible)

### development Profile
**Purpose**: Active development (most common)
**Allow**: Edit source files, write to src/tests/docs, git add/commit, all build tools
**Deny**: Sensitive files (.env*, *.key), dangerous commands (rm, sudo), force push, publish
**Rules**: ~68 allow, ~10 deny
**Safety**: High (protects secrets, prevents accidents)

### ci-cd Profile
**Purpose**: Continuous integration pipeline
**Allow**: Read all, build commands, test commands, git read-only
**Deny**: File editing, git push, publish commands
**Rules**: ~60 allow, ~15 deny
**Safety**: High (CI can build/test but not modify source)

### production Profile
**Purpose**: Production monitoring, read-only operations
**Allow**: Read all, git status/log, monitoring commands (ps, top, logs)
**Deny**: All editing, all writes, all build commands, git modifications
**Rules**: ~25 allow, ~20 deny
**Safety**: Maximum (strictest profile)

### documentation Profile
**Purpose**: Technical writing, docs-only work
**Allow**: Edit **.md, docs/**, Read all, git add/commit for docs
**Deny**: Edit source code, build commands
**Rules**: ~35 allow, ~12 deny
**Safety**: High (isolated to documentation)

### code-review Profile
**Purpose**: PR review, providing feedback
**Allow**: Read all, git read-only, comment tools
**Deny**: All editing (except maybe review comments), git commits
**Rules**: ~40 allow, ~15 deny
**Safety**: High (can review but not modify)

### testing Profile
**Purpose**: Test-driven development, QA
**Allow**: Edit test files, Read source, run tests (pytest, jest, cargo test)
**Deny**: Edit production source code
**Rules**: ~70 allow, ~12 deny
**Safety**: High (write tests, read source, no prod edits)

---

## Success Criteria

**Workflow complete when**:
- ✅ Profile identified from user request
- ✅ Profile loaded from permission_profiles.json
- ✅ All profile rules extracted (50-100 rules)
- ✅ User confirmation obtained (if required)
- ✅ Backup created (via apply_permissions.py)
- ✅ Validation passed (all rules)
- ✅ settings.json written in REPLACE mode
- ✅ User informed with comprehensive summary
- ✅ Restart reminder provided

---

## Token Budget Summary

**Typical profile application**:
```
Tier 1 (Metadata):            100 tokens ✅
Tier 2 (SKILL.md):          2,250 tokens ✅
profile-workflow:             800 tokens (this file)
permission_profiles.json:     200 tokens (surgical jq)
User confirmation:              0 tokens (interaction)
---
Total:                      3,350 tokens
Status:                     ✅ 66% under budget
```

**Profile with confirmation (read-only, production)**:
```
Tier 1 + 2 + this:          3,150 tokens ✅
Profile data:                 200 tokens
Confirmation interaction:      50 tokens
---
Total:                      3,400 tokens
Status:                     ✅ 66% under budget
```

---

## Integration with Other Workflows

**Profile as foundation**:
1. Apply profile (this workflow) → Sets baseline permissions
2. Add specific file patterns → file-pattern-workflow.md
3. Add specific CLI tool → cli-tool-workflow.md
4. Validate everything → validation-workflow.md

**Example Combination**:
```
1. Apply development profile (68 rules)
2. "also make **.proto editable" (file-pattern, +2 rules)
3. "enable docker" (cli-tool, +8 rules)
Total: 78 rules for custom development environment
```

---

## Next Steps After Workflow

**User must restart Claude Code** for permissions to take effect.

**Recommended actions**:
1. Test profile by editing a file or running a command
2. If too restrictive: Apply less restrictive profile or add specific permissions
3. If too broad: Apply more restrictive profile or add specific denies

**Optional follow-ups**:
- Validate: `python3 scripts/validate_config.py`
- Review: `cat settings.json` to see what was applied
- Rollback: See backup-restore-workflow.md if profile doesn't fit workflow

---

**End of Profile Application Workflow**
**Size**: ~450 lines (~2,250 tokens)
**Compliance**: ✅ Tier 3 (loaded on-demand only)
