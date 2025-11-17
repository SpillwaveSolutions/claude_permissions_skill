# File Pattern Permission Workflow

## Token Budget Tracker

**This Workflow**:
- Tier 1 (Metadata): 100 tokens ✅ (already loaded)
- Tier 2 (SKILL.md): 2,250 tokens ✅ (already loaded)
- This guide: ~1,000 tokens
- security_patterns.json (surgical): ~100 tokens
- **Estimated total**: 3,450 tokens
- **Status**: ✅ Within budget (<10,000)

---

## Purpose

Enable file editing/writing permissions based on natural language requests like:
- "make all markdown files editable"
- "allow editing TypeScript files in src/"
- "make docs folder writable"
- "enable Write for **.json files"

---

## Prerequisites

**This workflow triggered when**:
- User mentions file types: "markdown", ".md", "TypeScript", "**.rs", "JSON files"
- Keywords present: "make editable", "edit", "write", "modify", "allow writing"
- Pattern indicators: file extensions, glob patterns, directory names
- NOT a project setup request (that uses project-setup-workflow.md)

---

## Workflow Steps

### Step 1: Parse File Pattern

**Extract from user message**:
1. **File type** (e.g., "markdown", "TypeScript", "JSON")
2. **Directory scope** (e.g., "src/", "docs/", "all files")
3. **Operation** (edit vs write):
   - Edit: Modify existing files only
   - Write: Create new files + modify existing

**Natural Language → Glob Pattern Mapping**:

```
"markdown files" → **.md
"TypeScript files" → **.ts, **.tsx
"JavaScript" → **.js, **.jsx
"Python files" → **.py
"Rust files" → **.rs
"JSON files" → **.json
"YAML files" → **.yaml, **.yml
"config files" → **.toml, **.yaml, **.json, **.ini

"docs folder" → docs/**
"src directory" → src/**
"all files" → ** (use with caution)
"test files" → **/*.test.*, **/test_*.*, tests/**
```

**Specific file**:
```
"README.md" → README.md (exact match, no wildcards)
"package.json" → package.json
"Cargo.toml" → Cargo.toml
```

**Token Cost**: 0 tokens (in-memory pattern matching)

---

### Step 2: Determine Operations Needed

**Decision Logic**:

```
IF "edit" OR "modify" in request:
  Operations: [Edit(pattern), Read(pattern)]
  Reason: Edit requires reading first

IF "write" OR "create" OR "make writable" in request:
  Operations: [Write(pattern), Edit(pattern), Read(pattern)]
  Reason: Write implies edit + read

IF operation unclear:
  DEFAULT: [Edit(pattern), Read(pattern)]
  Reason: Edit is safer than Write (no new file creation)
```

**Examples**:
```
"make markdown editable" → Edit(**.md), Read(**.md)
"allow writing to docs/" → Write(docs/**), Edit(docs/**), Read(docs/**)
"edit TypeScript files" → Edit(**.ts), Edit(**.tsx), Read(**.ts), Read(**.tsx)
```

**Token Cost**: 0 tokens (in-memory logic)

---

### Step 3: Build Permission Rules

**Rule Construction**:

**Format**: `ToolName(pattern)`

**For single file type**:
```markdown
Request: "make markdown editable"

Rules:
- Edit(**.md)
- Read(**.md)
```

**For directory scope**:
```markdown
Request: "make docs folder writable"

Rules:
- Write(docs/**)
- Edit(docs/**)
- Read(docs/**)
```

**For multiple extensions**:
```markdown
Request: "edit TypeScript files"

Rules:
- Edit(**.ts)
- Edit(**.tsx)
- Read(**.ts)
- Read(**.tsx)
```

**For specific file**:
```markdown
Request: "make README.md editable"

Rules:
- Edit(README.md)
- Read(README.md)
```

**Glob Pattern Best Practices**:
- `**` = Match all subdirectories
- `*.ext` = Match in current directory only
- `**.ext` = Match in all subdirectories (most common)
- `dir/**` = Match everything in directory
- `dir/**.ext` = Match specific type in directory

**Token Cost**: 0 tokens (rule generation)

---

### Step 4: Apply Safety Rules

**CRITICAL: Check against security_patterns.json**:

```bash
jq '.recommended_deny_set.standard' references/security_patterns.json
```

**Token Cost**: ~100 tokens (surgical extraction)

**Blocked Patterns** (from security_patterns.json):
```
NEVER allow (even if user requests):
- Write(.env*)
- Write(*.key)
- Write(*.pem)
- Write(.aws/**)
- Write(.ssh/**)
- Write(.git/**)
- Edit(.env*)
- Edit(*.key)
- Edit(*.pem)
```

**Conflict Resolution**:

```
IF user requests pattern that matches deny rule:
  REMOVE that specific pattern from allow rules
  INFORM user of security restriction
  OFFER alternative (e.g., "You can edit .env.example instead")
```

**Example Conflict**:
```markdown
Request: "make all files in project editable"
Pattern: **

Safety Check:
- ** includes .env, *.key, *.pem (BLOCKED)

Action:
- Allow: Edit(**) ← Add to rules
- Deny: Edit(.env*), Edit(*.key), Edit(*.pem) ← Add deny rules
- Inform: "Enabled editing for all files except sensitive config (.env, keys)"
```

**Token Cost**: ~100 tokens (security patterns)

---

### Step 5: Execute apply_permissions.py

**Command Construction**:

```bash
python3 scripts/apply_permissions.py \
  --allow "Edit(**.md)" \
  --allow "Read(**.md)" \
  --deny "Edit(.env*)" \
  --deny "Write(*.key)"
```

**Script Actions** (automatic):
1. ✅ Create timestamped backup
2. ✅ Validate glob patterns (check syntax)
3. ✅ Detect conflicts (allow vs deny overlap)
4. ✅ Merge with existing settings.json
5. ✅ Write updated settings.json
6. ✅ Report changes

**Token Cost**: 0 tokens (script execution)

**Expected Output**:
```
✅ Backup created: settings.20250116_145530.backup
✅ Validation passed: 2 patterns are valid
✅ Added 2 allow rules, 0 deny rules
✅ Settings written successfully

Summary:
  Total allow rules: 17 (+2)
  Total deny rules: 8 (+0)
```

---

### Step 6: Confirm with User

**Report Format**:

```markdown
✅ **Made markdown files editable**

**Permissions added**:
- ✅ `Edit(**.md)` - Edit any .md file in project
- ✅ `Read(**.md)` - Read required for editing

**Files affected**:
- README.md
- docs/guide.md
- CHANGELOG.md
- (all .md files in project)

**Safety rules**:
- 🛡️ Sensitive files still protected (.env, *.key, *.pem)

**Backup created**: `settings.20250116_145530.backup`

**Next step**: Restart Claude Code for changes to take effect.
```

**Token Cost**: 0 tokens (output to user)

---

## Examples

### Example 1: Make Markdown Editable

**User Request**: "make all markdown files editable"

**Workflow Execution**:
1. Parse: Type=markdown, Scope=all, Operation=edit
2. Pattern: `**.md`
3. Operations: Edit + Read (edit implies read)
4. Build rules:
   ```
   Edit(**.md)
   Read(**.md)
   ```
5. Safety check: No conflicts (markdown is safe)
6. Execute: `python3 scripts/apply_permissions.py --allow "Edit(**.md)" --allow "Read(**.md)"`
7. Confirm: Report 2 rules added

**Total tokens**: 3,450 ✅

---

### Example 2: Make Docs Folder Writable

**User Request**: "make docs folder writable"

**Workflow Execution**:
1. Parse: Type=any, Scope=docs/, Operation=write
2. Pattern: `docs/**`
3. Operations: Write + Edit + Read (write implies all)
4. Build rules:
   ```
   Write(docs/**)
   Edit(docs/**)
   Read(docs/**)
   ```
5. Safety check: Ensure docs/ doesn't contain .env files
6. Execute: `python3 scripts/apply_permissions.py --allow "Write(docs/**)" --allow "Edit(docs/**)" --allow "Read(docs/**)"`
7. Confirm: Report 3 rules added for docs/ directory

**Total tokens**: 3,550 ✅

---

### Example 3: Edit TypeScript in src/

**User Request**: "allow editing TypeScript files in src/"

**Workflow Execution**:
1. Parse: Type=TypeScript (.ts, .tsx), Scope=src/, Operation=edit
2. Patterns: `src/**.ts`, `src/**.tsx`
3. Operations: Edit + Read
4. Build rules:
   ```
   Edit(src/**.ts)
   Edit(src/**.tsx)
   Read(src/**.ts)
   Read(src/**.tsx)
   ```
5. Safety check: TypeScript files are safe
6. Execute: `python3 scripts/apply_permissions.py --allow "Edit(src/**.ts)" --allow "Edit(src/**.tsx)" --allow "Read(src/**.ts)" --allow "Read(src/**.tsx)"`
7. Confirm: Report 4 rules added for TypeScript in src/

**Total tokens**: 3,550 ✅

---

### Example 4: Make Specific File Editable

**User Request**: "make README.md editable"

**Workflow Execution**:
1. Parse: Type=specific file, File=README.md, Operation=edit
2. Pattern: `README.md` (exact, no wildcards)
3. Operations: Edit + Read
4. Build rules:
   ```
   Edit(README.md)
   Read(README.md)
   ```
5. Safety check: README.md is safe
6. Execute: `python3 scripts/apply_permissions.py --allow "Edit(README.md)" --allow "Read(README.md)"`
7. Confirm: Report 2 rules added for README.md only

**Total tokens**: 3,450 ✅

---

### Example 5: Security Conflict - Attempt to Edit .env

**User Request**: "make all config files editable"

**Workflow Execution**:
1. Parse: Type=config (*.toml, *.yaml, *.json, .env*), Scope=all, Operation=edit
2. Patterns: `**.toml`, `**.yaml`, `**.json`, `.env*`
3. **Safety check detects**: `.env*` is in deny list
4. **REMOVE** .env* from allow patterns
5. Build rules:
   ```
   Edit(**.toml)
   Edit(**.yaml)
   Edit(**.json)
   Read(**.toml)
   Read(**.yaml)
   Read(**.json)

   Deny(Edit(.env*))  ← Safety rule
   Deny(Write(.env*))
   ```
6. Execute with filtered patterns
7. **Inform user**:
   ```
   ✅ Made config files editable

   Enabled:
   - **.toml files
   - **.yaml files
   - **.json files

   ⚠️ Security restriction:
   - .env files remain protected (contains secrets)
   - Alternative: Edit .env.example instead
   ```

**Total tokens**: 3,550 ✅

---

## Error Handling

### Error 1: Invalid glob pattern

**Detection**: apply_permissions.py validation fails

**Example Error**:
```
❌ Validation failed: Invalid glob pattern "**/.md" (leading dot after **)
Suggestion: Use "**.md" instead
```

**Action**:
1. Show error to user
2. Suggest corrected pattern
3. Offer to retry with correction

**Recovery**: Fix pattern and re-execute

---

### Error 2: Too broad pattern

**Detection**: Pattern is `**` or `*` (matches everything)

**Example**:
```
User: "make everything editable"
Pattern: **
```

**Action**:
1. **WARN user**: "This will make ALL files editable, including build outputs and dependencies"
2. **ASK user**: "Did you mean source files only? (yes/no)"
3. IF yes:
   - Suggest narrower pattern: `src/**`
   - Ask for project type to apply template
4. IF no (user confirms **):
   - Apply pattern with ALL security deny rules
   - Extra warning about build files

**Safety principle**: Always challenge overly broad patterns

---

### Error 3: Conflicting with existing rules

**Detection**: apply_permissions.py detects overlap

**Example**:
```
Existing: Edit(docs/*.md)
New request: Edit(docs/**)
```

**Action**:
1. Detect: New pattern is BROADER than existing
2. Replace old with new (user is expanding access)
3. Inform: "Expanded docs/*.md → docs/** (now includes subdirectories)"

**Alternative**:
```
Existing: Edit(docs/**)
New request: Edit(docs/*.md)
```

**Action**:
1. Detect: New pattern is NARROWER than existing
2. Keep existing (already has broader access)
3. Inform: "docs/** already enabled (includes *.md)"

---

### Error 4: File not found at runtime

**Detection**: User tries to edit file not matching pattern

**Example**:
```
User enabled: Edit(src/**.ts)
User tries to edit: config/app.ts
Error: Permission denied
```

**Action** (in user prompt after error):
1. Explain: "app.ts is in config/, not src/"
2. Offer: "Would you like to enable Edit(config/**.ts)?"
3. If yes: Run this workflow again with new pattern

**This is runtime guidance** - not part of this workflow execution

---

## Edge Cases

### Edge Case 1: Multiple file types in one request

**Example**: "make TypeScript and JavaScript files editable"

**Handling**:
1. Parse multiple types: [TypeScript, JavaScript]
2. Map to patterns: [**.ts, **.tsx, **.js, **.jsx]
3. Generate rules for ALL patterns:
   ```
   Edit(**.ts)
   Edit(**.tsx)
   Edit(**.js)
   Edit(**.jsx)
   Read(**.ts)
   Read(**.tsx)
   Read(**.js)
   Read(**.jsx)
   ```
4. Single apply_permissions.py execution with all rules
5. Report: "Enabled editing for TypeScript and JavaScript files (8 rules)"

**Token cost**: Same (~3,500 tokens)

---

### Edge Case 2: Nested directory scopes

**Example**: "make src/components writable"

**Handling**:
- Pattern: `src/components/**`
- This is CORRECT (nested paths work in glob patterns)
- Rules: Write(src/components/**), Edit(src/components/**), Read(src/components/**)

**No special handling needed** - glob patterns support nested paths

---

### Edge Case 3: Mixed operations

**Example**: "edit markdown but write to output.md specifically"

**Handling**:
1. Parse: Two distinct operations
2. Rules for "edit markdown":
   ```
   Edit(**.md)
   Read(**.md)
   ```
3. Additional rule for "write to output.md":
   ```
   Write(output.md)
   ```
4. Apply all together (3 rules total)

---

### Edge Case 4: File type ambiguity

**Example**: "make script files editable"

**Handling**:
1. "script" is ambiguous (.sh, .py, .js, .rb?)
2. **ASK user**: "Which script type? (Shell .sh, Python .py, JavaScript .js, Ruby .rb, or all?)"
3. Wait for clarification
4. Apply specific patterns based on user choice

**Don't guess** - always clarify ambiguous file types

---

## Success Criteria

**Workflow complete when**:
- ✅ File pattern parsed correctly
- ✅ Glob pattern(s) generated
- ✅ Operations determined (Edit, Write, Read)
- ✅ Permission rules built
- ✅ Safety rules checked (no sensitive files)
- ✅ Backup created (via apply_permissions.py)
- ✅ Validation passed (glob syntax)
- ✅ settings.json written successfully
- ✅ User informed with specific files affected
- ✅ Restart reminder provided

---

## Token Budget Summary

**Typical file pattern request**:
```
Tier 1 (Metadata):          100 tokens ✅
Tier 2 (SKILL.md):        2,250 tokens ✅
file-pattern-workflow.md: 1,000 tokens (this file)
security_patterns.json:     100 tokens (surgical)
Script execution:             0 tokens
---
Total:                    3,450 tokens
Status:                   ✅ 65% under budget
```

**Complex request (multiple types + directory scope)**:
```
Tier 1 + 2 + this:        3,350 tokens ✅
security_patterns.json:     100 tokens
Additional logic:           100 tokens
---
Total:                    3,550 tokens
Status:                   ✅ 64% under budget
```

---

## Next Steps After Workflow

**User must restart Claude Code** for permissions to take effect.

**Optional follow-ups**:
- Validate with: `python3 scripts/validate_config.py`
- Test by editing a file matching the pattern
- View what was added: `grep "Edit(" settings.json`
- Rollback if needed: See guides/workflows/backup-restore-workflow.md

---

## Related Workflows

**If user says**:
- "setup TypeScript project" → Use project-setup-workflow.md (applies template)
- "enable git" → Use cli-tool-workflow.md (different purpose)
- "apply development profile" → Use profile-application-workflow.md (bulk changes)

**This workflow is for**: Specific file pattern permission requests only

---

**End of File Pattern Workflow**
**Size**: ~420 lines (~2,100 tokens)
**Compliance**: ✅ Tier 3 (loaded on-demand only)
