# Project Setup Permission Workflow

## Token Budget Tracker

**This Workflow**:
- Tier 1 (Metadata): 100 tokens ✅ (already loaded)
- Tier 2 (SKILL.md): 2,250 tokens ✅ (already loaded)
- This guide: ~1,500 tokens
- project_templates.json (surgical): ~200 tokens
- security_patterns.json (surgical): ~100 tokens
- **Estimated total**: 4,150 tokens
- **Status**: ✅ Within budget (<10,000)

---

## Purpose

Apply comprehensive permission templates for specific project types:
- "this is a Rust project, setup permissions"
- "configure for TypeScript development"
- "setup Java Maven project"
- "apply Python project template"

**Key difference from file-pattern-workflow**:
- This applies **full templates** (20-30 rules per language)
- file-pattern-workflow applies **specific patterns** (2-5 rules)

---

## Prerequisites

**This workflow triggered when**:
- User mentions project type: "Rust", "Java", "TypeScript", "Python", "Go", etc.
- Keywords: "setup", "configure", "this is a X project", "apply template"
- User wants comprehensive permissions, not just file editing
- May follow auto-detection from detect_project.py

---

## Supported Project Types

**Pre-configured templates** (in project_templates.json):

| Language | Indicator Files | Template Includes |
|----------|----------------|-------------------|
| Rust | Cargo.toml | src/**.rs, cargo commands, target/ deny |
| Java Maven | pom.xml | src/**.java, mvn commands, target/ deny |
| Java Gradle | build.gradle* | src/**.java, gradle commands, build/ deny |
| TypeScript | tsconfig.json | src/**.ts, **.tsx, npm/yarn, node_modules/ deny |
| JavaScript | package.json (no tsconfig) | src/**.js, **.jsx, npm commands |
| Python | pyproject.toml, setup.py | **.py, pytest, pip, __pycache__/ deny |
| Go | go.mod | **.go, go build/test, vendor/ deny |
| Ruby | Gemfile | **.rb, bundle, vendor/ deny |
| PHP | composer.json | **.php, composer, vendor/ deny |
| C# | *.csproj, *.sln | **.cs, dotnet, bin/obj/ deny |
| C++ | CMakeLists.txt | **.cpp, **.h, cmake, build/ deny |
| Swift | Package.swift | **.swift, swift build/test |

---

## Workflow Steps

### Step 1: Determine Project Type

**Three methods**:

**Method A: User explicitly states**:
```
"this is a Rust project" → Type: rust
"setup TypeScript" → Type: typescript
"configure Java Maven" → Type: java-maven
```

**Method B: Auto-detection via detect_project.py**:
```bash
python3 scripts/detect_project.py
```

**Example Output**:
```json
{
  "detected_types": ["rust"],
  "confidence": "high",
  "indicator_files": ["Cargo.toml", "Cargo.lock"],
  "suggestions": [
    "Apply Rust template for src/**.rs editing",
    "Enable cargo commands (build, test, run)",
    "Deny target/ directory (build outputs)"
  ]
}
```

**Method C: Ask user if ambiguous**:
```
Detected: package.json + tsconfig.json
Question: "Is this a TypeScript or JavaScript project?"
Wait for user clarification
```

**Token Cost**:
- Method A (explicit): 0 tokens (parsing)
- Method B (auto-detect): 0 tokens (script execution)
- Method C (ask user): 0 tokens (user interaction)

---

### Step 2: Load Template for Project Type

**Surgical extraction from project_templates.json**:

```bash
jq '.LANGUAGE_KEY' references/project_templates.json
```

**Examples**:

**For Rust**:
```bash
jq '.rust' references/project_templates.json
```

**For TypeScript**:
```bash
jq '.typescript' references/project_templates.json
```

**For Python**:
```bash
jq '.python' references/project_templates.json
```

**Token Cost**: ~200 tokens (vs 1,955 for full file = 90% savings)

---

### Step 3: Extract Template Rules

**Template Structure**:

```json
{
  "rust": {
    "description": "Rust development with Cargo",
    "file_patterns": {
      "allow": [
        "Edit(src/**.rs)",
        "Edit(Cargo.toml)",
        "Edit(Cargo.lock)",
        "Read(**.rs)",
        "Read(Cargo.*)"
      ],
      "deny": [
        "Write(target/**)",
        "Edit(target/**)"
      ]
    },
    "commands": {
      "allow": [
        "Bash(cargo build *)",
        "Bash(cargo test *)",
        "Bash(cargo run *)",
        "Bash(cargo check *)",
        "Bash(cargo clippy *)",
        "Bash(cargo doc *)"
      ],
      "deny": [
        "Bash(cargo publish *)",
        "Bash(cargo install *)"
      ]
    },
    "common_tools": {
      "allow": [
        "Bash(git status *)",
        "Bash(git log *)",
        "Bash(git diff *)"
      ]
    }
  }
}
```

**Rule Extraction**:
1. Combine all "allow" arrays → allow_rules list
2. Combine all "deny" arrays → deny_rules list
3. Total rules: Typically 20-35 per language template

**Token Cost**: 0 tokens (already loaded in Step 2 jq output)

---

### Step 4: Apply Universal Safety Rules

**Load security_patterns.json**:

```bash
jq '.recommended_deny_set.standard' references/security_patterns.json
```

**Token Cost**: ~100 tokens (surgical)

**Merge with template deny rules**:

```
Template deny rules (from project_templates.json):
  - Write(target/**)
  - Bash(cargo publish *)

Universal safety rules (from security_patterns.json):
  - Read(.env*)
  - Write(*.key)
  - Bash(rm *)
  - Bash(sudo *)

Combined deny rules:
  - All template denies
  - All universal safety denies
  - No duplicates (deduplicated by apply_permissions.py)
```

**Token Cost**: ~100 tokens (security patterns)

---

### Step 5: Execute apply_permissions.py

**Command Construction** (example for Rust):

```bash
python3 scripts/apply_permissions.py \
  --allow "Edit(src/**.rs)" \
  --allow "Edit(Cargo.toml)" \
  --allow "Read(**.rs)" \
  --allow "Bash(cargo build *)" \
  --allow "Bash(cargo test *)" \
  --allow "Bash(cargo run *)" \
  --allow "Bash(git status *)" \
  --deny "Write(target/**)" \
  --deny "Bash(cargo publish *)" \
  --deny "Read(.env*)" \
  --deny "Bash(rm *)" \
  --deny "Bash(sudo *)"
```

**Script Actions** (automatic):
1. ✅ Create timestamped backup
2. ✅ Validate all 20-35 rules
3. ✅ Merge with existing settings.json (preserve user customizations)
4. ✅ Deduplicate rules
5. ✅ Write updated settings.json
6. ✅ Report summary

**Token Cost**: 0 tokens (script execution)

**Expected Output**:
```
✅ Backup created: settings.20250116_151045.backup
✅ Validation passed: All 28 rules are valid
✅ Added 18 allow rules, 10 deny rules
✅ Settings written successfully

Summary:
  Total allow rules: 35 (+18)
  Total deny rules: 18 (+10)
```

---

### Step 6: Confirm with User

**Report Format** (example for Rust):

```markdown
✅ **Rust project permissions configured**

**File editing enabled**:
- ✅ `src/**.rs` - All Rust source files
- ✅ `Cargo.toml` - Project manifest
- ✅ `Cargo.lock` - Dependency lock file
- ✅ `**.md` - Documentation files

**Commands enabled**:
- ✅ `cargo build` - Compile project
- ✅ `cargo test` - Run tests
- ✅ `cargo run` - Execute binary
- ✅ `cargo check` - Fast compile check
- ✅ `cargo clippy` - Linter
- ✅ `cargo doc` - Generate docs
- ✅ `git` read-only commands (status, log, diff)

**Protected patterns**:
- 🛡️ `target/**` - Build outputs (no editing)
- 🛡️ `cargo publish` - No accidental publishing
- 🛡️ `.env*`, `*.key`, `*.pem` - Sensitive files
- 🛡️ `rm`, `sudo` - Dangerous commands

**Total rules**: 18 allow, 10 deny

**Backup created**: `settings.20250116_151045.backup`

**Next step**: Restart Claude Code for changes to take effect.
```

**Token Cost**: 0 tokens (output to user)

---

## Examples

### Example 1: Setup Rust Project

**User Request**: "this is a Rust project, setup permissions"

**Workflow Execution**:
1. Determine type: rust (explicit from user)
2. Load template: `jq '.rust' references/project_templates.json`
3. Extract rules:
   - Allow: 12 file patterns + 6 cargo commands + 3 git commands
   - Deny: 2 cargo denies + 8 universal safety denies
4. Apply safety: Merge deny rules (10 total)
5. Execute: `python3 scripts/apply_permissions.py` with 21 allow, 10 deny
6. Confirm: Report comprehensive Rust setup

**Total tokens**: 4,150 ✅

---

### Example 2: Auto-Detect TypeScript Project

**User Request**: "setup this project for editing"

**Workflow Execution**:
1. Run: `python3 scripts/detect_project.py`
   ```json
   {
     "detected_types": ["typescript"],
     "confidence": "high",
     "indicator_files": ["package.json", "tsconfig.json"]
   }
   ```
2. Inform user: "Detected TypeScript project. Applying template..."
3. Load template: `jq '.typescript' references/project_templates.json`
4. Extract rules:
   - Allow: src/**.ts, **.tsx, npm/yarn commands, tsconfig.json editing
   - Deny: node_modules/**, dist/**, npm publish
5. Apply safety: Add .env*, *.key denies
6. Execute: `python3 scripts/apply_permissions.py` with ~25 rules
7. Confirm: Report TypeScript setup complete

**Total tokens**: 4,150 ✅

---

### Example 3: Java Maven vs Gradle Detection

**User Request**: "configure Java project"

**Workflow Execution**:
1. Run: `python3 scripts/detect_project.py`
   ```json
   {
     "detected_types": ["java-maven"],
     "confidence": "high",
     "indicator_files": ["pom.xml"]
   }
   ```
2. Detected: Maven (not Gradle)
3. Load template: `jq '."java-maven"' references/project_templates.json`
4. Extract rules:
   - Allow: src/**.java, pom.xml, mvn commands (compile, test, package)
   - Deny: target/**, mvn deploy
5. Apply safety rules
6. Execute: Apply Maven-specific permissions
7. Confirm: "Java Maven project configured"

**Total tokens**: 4,200 ✅

**Alternative** (if build.gradle found):
- Template: `jq '."java-gradle"' references/project_templates.json`
- Commands: gradle commands instead of mvn
- Deny: build/** instead of target/**

---

### Example 4: Python Project with Multiple Tools

**User Request**: "setup Python project"

**Workflow Execution**:
1. Type: python (explicit)
2. Load template: `jq '.python' references/project_templates.json`
3. Extract rules:
   - Allow: **.py, pyproject.toml, setup.py, requirements.txt
   - Allow: pytest, pip install (dependencies only), python commands
   - Deny: __pycache__/**, *.pyc, pip uninstall
4. Apply safety: .env*, *.key
5. Execute: Apply comprehensive Python permissions
6. Confirm: Report includes pytest, pip, python3 commands enabled

**Total tokens**: 4,150 ✅

---

### Example 5: Ambiguous Project - Multiple Languages

**Scenario**: Project has both Rust and Python files

**Workflow Execution**:
1. Run: `python3 scripts/detect_project.py`
   ```json
   {
     "detected_types": ["rust", "python"],
     "confidence": "medium",
     "indicator_files": ["Cargo.toml", "setup.py"]
   }
   ```
2. **ASK user**: "Detected Rust and Python. Which is the primary language?"
3. User responds: "Rust (with Python scripts)"
4. **Apply Rust template** as primary
5. **Add Python subset** for **.py files + python3 command
6. Execute: Combined ruleset (Rust full + Python subset)
7. Confirm: "Configured for Rust with Python scripting support"

**Total tokens**: 4,300 ✅

---

## Error Handling

### Error 1: Unknown project type

**Detection**: User mentions language not in project_templates.json

**Example**: "setup Perl project"

**Action**:
1. Inform: "Perl template not available in pre-configured templates"
2. Offer: "I can create custom permissions for Perl. What files need editing? (e.g., **.pl, **.pm)"
3. Route to: file-pattern-workflow.md for custom setup
4. Suggest: Research workflow if user wants tool-specific permissions

**Recovery**: Use file-pattern-workflow for manual template creation

---

### Error 2: No indicator files found

**Detection**: detect_project.py returns empty

**Example Output**:
```json
{
  "detected_types": [],
  "confidence": "none",
  "indicator_files": [],
  "suggestions": [
    "No recognized project structure found",
    "Check if this is a monorepo or unconventional layout"
  ]
}
```

**Action**:
1. Inform user: "Could not auto-detect project type"
2. **ASK**: "What language/framework is this project? (Rust, Java, TypeScript, Python, Go, etc.)"
3. Wait for user response
4. Proceed with explicit type from Step 1

**Recovery**: User provides explicit type

---

### Error 3: Conflicting with existing rules

**Detection**: apply_permissions.py detects overlap

**Example**:
```
Existing: Edit(src/main.rs)
Template: Edit(src/**.rs)
```

**Action**:
1. Template rule is BROADER → Replace existing
2. Inform: "Expanded src/main.rs → src/**.rs (now includes all Rust files)"
3. Preserve any user custom denies

**Policy**: Template rules override existing patterns when broader

---

### Error 4: Template validation fails

**Detection**: apply_permissions.py validation error on template rule

**Example Error**:
```
❌ Validation failed: Invalid tool name "BashOutput" in template
```

**Action**:
1. **CRITICAL**: This indicates template database corruption
2. Report error to user: "Template database error. Please file issue at GitHub."
3. Offer: "Use file-pattern-workflow for manual setup as workaround"
4. Log: Record which template failed for bug report

**Recovery**: Fallback to manual file-pattern workflow

---

## Edge Cases

### Edge Case 1: Monorepo with multiple projects

**Example**: workspace/ with both Rust and TypeScript sub-projects

**Handling**:
1. detect_project.py finds both
2. **ASK user**: "This is a monorepo. Which project are you working on?"
3. Options:
   - "Rust project in services/api/" → Apply Rust template scoped to services/api/
   - "TypeScript project in web/" → Apply TypeScript template scoped to web/
   - "Both" → Apply BOTH templates with directory scoping
4. Scope patterns:
   ```
   Rust: Edit(services/api/src/**.rs)
   TypeScript: Edit(web/src/**.ts)
   ```

**Token cost**: Same (~4,200 tokens)

---

### Edge Case 2: Legacy project structure

**Example**: Java project without pom.xml or build.gradle (just *.java files)

**Handling**:
1. detect_project.py finds **.java but no build files
2. Confidence: low
3. **ASK user**: "Found Java files but no Maven/Gradle. Is this a legacy project?"
4. If yes:
   - Apply Java file patterns only (**.java)
   - Skip build tool commands
   - Warn: "No build tool detected. Add Maven/Gradle for full template."

**Fallback**: Partial template (files only, no commands)

---

### Edge Case 3: User wants ONLY files, not commands

**Example**: "setup Rust files but don't enable cargo commands"

**Handling**:
1. Load Rust template
2. **Filter**: Extract only file_patterns.allow, skip commands.allow
3. Apply:
   ```
   Allow: Edit(src/**.rs), Edit(Cargo.toml), Read(**.rs)
   Deny: (safety rules only, no command denies)
   ```
4. Inform: "Enabled Rust file editing. Cargo commands NOT enabled."

**Use case**: Users who prefer manual terminal control

---

### Edge Case 4: Template override - User customization

**Example**: User previously customized Rust deny rules, now applying template

**Handling**:
1. apply_permissions.py detects existing custom rules
2. **Preserve** user customizations that don't conflict
3. **Merge** template with custom rules
4. Inform: "Applied Rust template + preserved your custom deny rules"

**Policy**: User customizations always win over template defaults

---

## Success Criteria

**Workflow complete when**:
- ✅ Project type determined (auto-detect or explicit)
- ✅ Template loaded from project_templates.json
- ✅ All template rules extracted (files + commands)
- ✅ Universal safety rules applied
- ✅ Backup created (via apply_permissions.py)
- ✅ Validation passed (all 20-35 rules)
- ✅ settings.json written successfully
- ✅ User informed with comprehensive summary
- ✅ Restart reminder provided

---

## Token Budget Summary

**Typical project setup**:
```
Tier 1 (Metadata):          100 tokens ✅
Tier 2 (SKILL.md):        2,250 tokens ✅
project-setup-workflow:   1,500 tokens (this file)
project_templates.json:     200 tokens (surgical jq)
security_patterns.json:     100 tokens (surgical jq)
detect_project.py output:     0 tokens (script execution)
---
Total:                    4,150 tokens
Status:                   ✅ 58% under budget
```

**Complex project (monorepo, multiple types)**:
```
Tier 1 + 2 + this:        3,850 tokens ✅
Templates (2 languages):    400 tokens
Security patterns:          100 tokens
User interaction:            50 tokens
---
Total:                    4,400 tokens
Status:                   ✅ 56% under budget
```

---

## Integration with Other Workflows

**After project setup, user might**:

1. **Add specific file** → Use file-pattern-workflow.md
   - Example: "also make **.toml editable" (in addition to Cargo.toml)

2. **Enable additional CLI tool** → Use cli-tool-workflow.md
   - Example: "enable docker" (for containerized Rust builds)

3. **Apply profile on top** → Use profile-application-workflow.md
   - Example: "apply ci-cd profile" (for automated testing)

**Template is foundation** - other workflows add incremental permissions

---

## Next Steps After Workflow

**User must restart Claude Code** for permissions to take effect.

**Recommended testing**:
1. Try editing a source file in the project
2. Run a build command (cargo build, npm test, mvn compile)
3. Verify deny rules work (try editing target/ or node_modules/)

**Optional follow-ups**:
- Validate: `python3 scripts/validate_config.py`
- Review: `grep "Edit(" settings.json | grep "LANGUAGE_EXTENSION"`
- Expand: Add more specific patterns via file-pattern-workflow

---

**End of Project Setup Workflow**
**Size**: ~550 lines (~2,750 tokens)
**Compliance**: ✅ Tier 3 (loaded on-demand only)
