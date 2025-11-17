---
name: claude-permissions
description: |
  Proactive Claude Code permission manager. Configures permissions via natural language for CLI tools (git, gcloud, aws, kubectl, maven, gradle, npm, docker), project types (Rust, Java, TypeScript, Python), and file patterns. Auto-detects project types and researches unknown tools.
version: 1.0.0
category: automation
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - mcp__perplexity-ask__perplexity_ask
  - mcp__brave-search__brave_web_search
  - WebSearch
  - Skill
tier1_token_budget: 100
tier2_token_budget: 2500
---

# Claude Permissions Manager

## Quick Reference

**Purpose**: Auto-configure Claude Code permissions via natural language
**Token Budget**: T1(100) + T2(2,500) + T3(1,500-3,000 per workflow)
**Architecture**: Progressive Disclosure (3-tier) - Load only what's needed

---

## Intent Classification Decision Tree

### Step 1: Detect Request Type

Parse user message for patterns:

**CLI Tool Request** → Indicators:
- Keywords: "enable", "allow", "configure" + tool name
- Tool names: git, gcloud, aws, kubectl, docker, npm, pip, maven, gradle, cargo, helm, terraform, pulumi, ansible, claude, gemini
- Modes: "read", "write", "read-only", "commits", "pushes"
- **Route to**: `guides/workflows/cli-tool-workflow.md`

**File Pattern Request** → Indicators:
- Keywords: "make editable", "edit", "write" + file type/pattern
- Patterns: "**.md", "TypeScript files", "src/", "docs folder"
- **Route to**: `guides/workflows/file-pattern-workflow.md`

**Project Type Request** → Indicators:
- Keywords: "this is a [language] project", "setup", "project"
- Languages: Rust, Java, TypeScript, Python, Go, Ruby, PHP, C#, C++, Swift
- **Route to**: `guides/workflows/project-setup-workflow.md`

**Profile Request** → Indicators:
- Keywords: "apply profile", "use profile" + profile name
- Profiles: read-only, development, ci-cd, production, documentation, code-review, testing
- **Route to**: `guides/workflows/profile-application-workflow.md`

**Validation/Troubleshooting** → Indicators:
- Keywords: "validate", "check", "troubleshoot", "not working"
- **Route to**: `guides/workflows/validation-workflow.md`

**Backup/Restore** → Indicators:
- Keywords: "backup", "restore", "rollback", "undo"
- **Route to**: `guides/workflows/backup-restore-workflow.md`

### Step 2: Load Appropriate Workflow

**CRITICAL**: Load ONLY the workflow guide needed. Do NOT load multiple guides.

```
IF CLI Tool Request:
  Read guides/workflows/cli-tool-workflow.md
  Token cost: +1,500

IF File Pattern Request:
  Read guides/workflows/file-pattern-workflow.md
  Token cost: +1,200

IF Project Type Request:
  Read guides/workflows/project-setup-workflow.md
  Token cost: +1,800

IF Profile Request:
  Read guides/workflows/profile-application-workflow.md
  Token cost: +1,000

IF Validation:
  Read guides/workflows/validation-workflow.md
  Token cost: +1,200

IF Backup/Restore:
  Read guides/workflows/backup-restore-workflow.md
  Token cost: +750
```

**Unknown Tool Detection**: If CLI tool mentioned but not in known list → Load research workflow:
```
Read guides/workflows/research-workflow.md
Token cost: +2,000
```

---

## Core Detection Logic

### CLI Tool Recognition

**Known Tools** (check against `references/cli_commands.json`):
- Version Control: git
- Cloud: gcloud, aws, az
- Containers: docker, kubectl, helm
- Build: npm, pip, maven, gradle, cargo, go, yarn, bundle, composer
- Infrastructure: terraform, pulumi, ansible
- AI: claude, gemini

**Mode Detection**:
- Contains "read", "list", "show", "describe" → READ mode (safer default)
- Contains "write", "push", "commit", "deploy", "publish" → WRITE mode
- No mode → Default to READ

**Tool Lookup**:
1. Check if tool in `references/cli_commands.json` (use grep)
2. If found → Extract commands for detected mode
3. If NOT found → Route to research workflow

### Project Type Detection

**Auto-Detection** (via file scanning):
```
Cargo.toml                      → Rust
pom.xml                         → Java Maven
build.gradle*                   → Java Gradle
package.json + tsconfig.json    → TypeScript
package.json (alone)            → JavaScript
pyproject.toml | setup.py       → Python
go.mod                          → Go
Gemfile                         → Ruby
composer.json                   → PHP
*.csproj | *.sln                → C#
CMakeLists.txt                  → C++
Package.swift                   → Swift
```

**Detection Method**: Run `scripts/detect_project.py` or scan for indicator files

### Profile Recognition

**Available Profiles** (from `assets/permission_profiles.json`):
- `read-only` - Code review, security audit
- `development` - Active development (most common)
- `ci-cd` - Continuous integration
- `production` - Monitoring only
- `documentation` - Docs writing
- `code-review` - PR review
- `testing` - TDD workflow

---

## Resource Loading Policy - CRITICAL

**NEVER load resources proactively or "just in case"**

### Loading Workflow Guides

**DO**: Load specific workflow when decision tree routes to it
```bash
Read guides/workflows/{workflow-name}.md
```

**DON'T**: Load all guides upfront or multiple guides

### Loading Reference Data - Surgical Only

**CLI Commands** (one tool only):
```bash
grep -A 25 '"git"' references/cli_commands.json
# Token cost: ~150 tokens (vs 2,650 for full file)
```

**Project Templates** (one language only):
```bash
jq '.rust' references/project_templates.json
# Token cost: ~200 tokens (vs 1,955 for full file)
```

**Security Patterns** (one level only):
```bash
jq '.recommended_deny_set.standard' references/security_patterns.json
# Token cost: ~100 tokens (vs 805 for full file)
```

**Permission Profiles** (one profile only):
```bash
jq '.development' assets/permission_profiles.json
# Token cost: ~200 tokens (vs 1,240 for full file)
```

### Executing Scripts

**ONLY execute when workflow instructs**:

**detect_project.py** - When:
- Project type ambiguous
- User says "make editable" without specifying language
- Need to recommend permissions

**apply_permissions.py** - When:
- All permission rules gathered
- Ready to apply changes
- Handles backup, validation, writing automatically

**validate_config.py** - When:
- User requests validation
- After complex permission changes
- Troubleshooting issues

---

## Safety Rules - Always Apply

**Every permission operation MUST**:

1. **Load security patterns**:
   ```bash
   jq '.recommended_deny_set.standard' references/security_patterns.json
   ```

2. **Apply minimum deny rules** (from security patterns):
   - `Read(.env*)`
   - `Read(*.key)`
   - `Read(*.pem)`
   - `Read(.aws/**)`
   - `Read(.ssh/**)`
   - `Write(.env*)`
   - `Bash(rm *)`
   - `Bash(sudo *)`
   - `Bash(git push * --force)`
   - Plus 4 more (13 total for "standard" level)

3. **Create backup** before any settings write:
   - Automatic via `scripts/apply_permissions.py`
   - Format: `settings.YYYYMMDD_HHMMSS.backup`

4. **Validate syntax** before applying:
   - Automatic via `scripts/apply_permissions.py`
   - Checks tool names, patterns, conflicts

---

## Token Budget Management

**Budget Tiers**:
- Simple request (CLI tool): <5,000 tokens
- Medium request (project setup): <7,000 tokens
- Complex request (unknown tool): <10,000 tokens
- Warning threshold: >10,000 tokens

**Tracking Template**:
```
Token Budget Status:
- Tier 1 (Metadata): 100 tokens ✅
- Tier 2 (SKILL.md): 2,250 tokens ✅
- Workflow Guide: +1,500 tokens
- Reference Data: +200 tokens (surgical)
- Total: 4,050 tokens
- Status: ✅ Within budget (<10,000)
```

**Cost Optimization**:
- Use grep/jq for references (90% token savings)
- Load only needed workflow guide
- Execute scripts instead of explaining them
- Avoid loading examples unless requested

---

## Error Handling

**If workflow guide not found**:
- Proceed with best-effort inline logic
- Inform user of missing guide
- Suggest filing an issue

**If reference file not found**:
- Attempt operation without reference
- For unknown tools → use web search
- Warn user about limited functionality

**If script execution fails**:
- Show error message to user
- Suggest manual permission editing
- Provide settings file location

**If validation fails**:
- Report specific errors
- Suggest fixes
- Offer to restore from backup

---

## Skill Integration Points

**Other Skills** (invoke when appropriate):
- **gemini skill**: If user mentions "gemini CLI" and skill available
- None others currently applicable

**MCP Tools** (priority order for research):
1. `mcp__perplexity-ask__perplexity_ask` (preferred)
2. `mcp__brave-search__brave_web_search` (fallback)
3. `WebSearch` (final fallback)

---

## Success Criteria Checklist

Permission operation complete when:
- ✅ Backup created (timestamped)
- ✅ Permissions validated (syntax + conflicts)
- ✅ Safety rules applied (deny patterns)
- ✅ Settings written successfully
- ✅ User informed of changes
- ✅ Restart reminder provided

---

## Workflow Guide Manifest

**Available workflows** (in `guides/workflows/`):

| Workflow | File | Token Cost | Use Case |
|----------|------|------------|----------|
| CLI Tool | cli-tool-workflow.md | ~1,500 | Enable git, gcloud, etc. |
| File Pattern | file-pattern-workflow.md | ~1,200 | Make files editable |
| Project Setup | project-setup-workflow.md | ~1,800 | Setup Rust, Java, etc. |
| Profile | profile-application-workflow.md | ~1,000 | Apply dev/ci-cd profile |
| Research | research-workflow.md | ~2,000 | Unknown tool discovery |
| Validation | validation-workflow.md | ~1,200 | Troubleshoot issues |
| Backup/Restore | backup-restore-workflow.md | ~750 | Rollback changes |

**Load these ONLY when decision tree routes to them.**

---

## Reference File Manifest

**Available references** (load surgically with grep/jq):

| Reference | File | Full Size | Surgical Size | Savings |
|-----------|------|-----------|---------------|---------|
| CLI Tools | cli_commands.json | 2,650 tokens | ~150 | 94% |
| Project Templates | project_templates.json | 1,955 tokens | ~200 | 90% |
| Security Patterns | security_patterns.json | 805 tokens | ~100 | 88% |
| Profiles | permission_profiles.json | 1,240 tokens | ~200 | 84% |

**Total potential savings**: ~5,000 tokens per request through surgical loading

---

## Quick Start Examples

**Enable git (read-only)**:
1. Detect: CLI tool request (git, read mode)
2. Load: `guides/workflows/cli-tool-workflow.md`
3. Execute workflow → Auto-adds safe git commands

**Make markdown editable**:
1. Detect: File pattern request (**.md)
2. Load: `guides/workflows/file-pattern-workflow.md`
3. Execute workflow → Adds Write/Edit permissions

**Setup TypeScript project**:
1. Detect: Project type request (TypeScript)
2. Load: `guides/workflows/project-setup-workflow.md`
3. Auto-detect or confirm → Apply TypeScript template

**Apply development profile**:
1. Detect: Profile request (development)
2. Load: `guides/workflows/profile-application-workflow.md`
3. Execute workflow → Bulk apply dev permissions

---

## Next Steps for Claude

**Every request follows this pattern**:

1. **Classify intent** using decision tree (Step 1)
2. **Route to workflow** using routing logic (Step 2)
3. **Load workflow guide** from guides/workflows/
4. **Follow workflow** step-by-step as documented
5. **Load references** only as workflow instructs (surgical)
6. **Execute scripts** when workflow requires
7. **Track token budget** throughout
8. **Complete operation** per success criteria
9. **Inform user** of changes and next steps

**Remember**:
- ✅ Load only needed workflow (not all 7)
- ✅ Use grep/jq for references (not full files)
- ✅ Execute scripts for heavy lifting
- ✅ Track token costs
- ✅ Apply safety rules always
- ✅ Create backups before changes

---

**End of Tier 2 (SKILL.md)**
**Size**: ~450 lines (~2,250 tokens)
**Reduction**: 861 → 450 lines (48% reduction)
**PDA Compliant**: ✅ Under 500 line budget
