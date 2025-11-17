---
name: claude-permissions
description: |
  Proactive Claude Code permission manager that automatically configures read/write permissions based on natural language requests. This skill should be used when users want to enable CLI tools (git, gcloud, aws, kubectl, maven, gradle, npm, docker, etc.), make file types editable, or streamline permission management. Automatically detects project types (Rust, Java, TypeScript, Python, etc.) and applies appropriate file editing permissions. Uses web search and AI tools to research unknown commands when needed. Triggers on permission-related requests, CLI tool mentions, or project setup scenarios.
version: 1.0.0
category: automation
triggers:
  - permissions
  - claude-permissions
  - enable
  - make editable
  - allow
  - git
  - gcloud
  - aws
  - kubectl
  - maven
  - gradle
  - npm
  - docker
  - rust project
  - java project
  - typescript project
  - python project
  - enable editing
  - configure permissions
  - add permissions
author: Claude Code Community
license: MIT
tags:
  - automation
  - permissions
  - cli-tools
  - configuration
  - project-setup
  - security
---

# Claude Permissions Manager

## Overview

Intelligent permission manager that automatically configures Claude Code permissions based on natural language requests. Eliminates friction by understanding user intent and applying appropriate read/write permissions for CLI tools and file patterns. Always prioritizes safety with built-in deny rules for sensitive files.

## Core Capabilities

### 1. Natural Language Permission Requests

Parse user intent from natural language and apply appropriate permissions:

**CLI Tool Requests:**
- "enable git" → Adds read-only git commands (status, log, diff, show, branch, remote)
- "enable git commits and pushes" → Adds write git operations (commit, push, pull, add, merge, rebase) + deny rule for `--force`
- "enable gcloud read commands" → Adds gcloud list/describe/get-iam-policy operations
- "enable kubectl" → Adds read-only kubernetes commands (get, describe, logs)
- "enable docker" → Adds read-only docker commands (ps, images, logs, inspect)

**File Pattern Requests:**
- "make all markdown files editable" → Adds `Write(**.md)`, `Edit(**.md)`, `Read(**.md)`
- "enable editing TypeScript files" → Adds `Write(**.ts)`, `Write(**.tsx)`, `Edit(**.ts)`, `Edit(**.tsx)`
- "make docs folder editable" → Adds `Write(docs/**)`, `Edit(docs/**)`

**Project Type Requests:**
- "this is a Rust project, make it editable" → Auto-detects Cargo.toml + adds Rust permissions
- "enable Java editing" → Adds Java file patterns + maven/gradle commands
- "set up TypeScript project" → Adds TypeScript + npm permissions

### 2. Built-in CLI Tool Knowledge

Pre-configured understanding of read-only vs write operations for major tools:

**Git:**
- Read: `status`, `log`, `diff`, `show`, `branch`, `remote`, `config --list`
- Write: `commit`, `push`, `pull`, `add`, `merge`, `rebase`, `reset`, `checkout`, `tag`
- Dangerous: `push --force`, `reset --hard`, `clean -fd`

**GCP (gcloud):**
- Read: `list`, `describe`, `get-iam-policy`
- Write: `create`, `delete`, `update`, `deploy`, `set`, `add-iam-policy-binding`, `remove-iam-policy-binding`

**AWS CLI:**
- Read: `describe-*`, `list-*`, `get-*`
- Write: `create-*`, `delete-*`, `update-*`, `put-*`

**Kubernetes (kubectl):**
- Read: `get`, `describe`, `logs`, `list` (RBAC verbs: get, list, watch)
- Write: `create`, `delete`, `apply`, `patch`, `edit`, `scale`, `rollout` (RBAC verbs: create, update, patch, delete)

**Maven:**
- Read: `compile`, `test`, `package`, `dependency:tree`, `help:*` (writes only to target/)
- Write: `install` (local repo), `deploy` (remote repo)

**Gradle:**
- Read: `tasks`, `dependencies`, `dependencyInsight`, `properties`, `-m` (dry-run)
- Write: `build`, `assemble`, `clean`, `test`, `publish`, `--write-locks`

**Docker:**
- Read: `ps`, `images`, `logs`, `inspect`, `stats`, `version`, `info`
- Write: `run`, `create`, `start`, `stop`, `rm`, `rmi`, `build`, `pull`, `push`

**npm:**
- Read: `list`, `view`, `search`, `audit`, `outdated`, `config list`
- Write: `install`, `update`, `publish`, `audit fix`, `uninstall`, `ci`

**pip:**
- Read: `list`, `show`, `freeze`, `check`, `search`, `debug`
- Write: `install`, `uninstall`, `download`, `wheel`

**Claude CLI:**
- Commands: `claude`, `-p` (print mode), `-c` (continue), `update`, `mcp`
- Slash commands: `/permissions`, `/config`, `/status`, `/allowed-tools`, `/mcp`, etc.

**Gemini CLI:**
- Slash commands: `/help`, `/chat`, `/settings`, `/mcp`, `/memory`, `/tools`, etc.
- Special: `@` (file injection), `!` (shell mode)

For complete CLI command reference, see `references/cli_commands.json`.

### 3. Auto-Detection of Project Types

Automatically detect project type by scanning for indicator files:

**Detection Logic:**
```
Cargo.toml → Rust project
pom.xml → Java Maven project
build.gradle / build.gradle.kts → Java Gradle project
package.json + tsconfig.json → TypeScript project
package.json (without tsconfig.json) → JavaScript project
pyproject.toml / setup.py / requirements.txt → Python project
go.mod → Go project
Gemfile → Ruby project
composer.json → PHP project
```

When project type is detected, automatically apply appropriate template from `references/project_templates.json`.

### 4. Research Mode for Unknown Tools

When encountering CLI tools not in the built-in database:

1. **Check Built-in Database** (`references/cli_commands.json`)
2. **If not found, research using:**
   - Perplexity Search: "What are read-only vs write operations for [tool]?"
   - Brave Web Search: Look up official documentation
   - Context7: Check framework/library docs if applicable
3. **Parse Results** to extract:
   - Read-only / safe operations
   - Write / destructive operations
   - Dangerous operations requiring extra caution
4. **Present to User** for confirmation before applying
5. **Optionally Cache** findings for future use

**Example Unknown Tool Workflow:**
```
User: "enable terraform read commands"
Claude:
  1. Checks cli_commands.json - not found
  2. Uses Perplexity: "terraform read-only vs write operations"
  3. Discovers: plan, show, validate, state list (read) vs apply, destroy (write)
  4. Presents: "Found these read-only terraform commands: plan, show, validate,
     state list, state show, output, version. Should I add these?"
  5. User confirms
  6. Applies permissions
```

### 5. Safety-First Design

**Always Include Deny Rules** for sensitive files and dangerous operations:

**Sensitive Files:**
```
Read(.env*)
Read(*.key)
Read(*.pem)
Read(.aws/**)
Read(.ssh/**)
Read(secrets/**)
Write(.env*)
Write(production.*)
```

**Dangerous Commands:**
```
Bash(rm *)
Bash(sudo *)
Bash(chmod *)
Bash(chown *)
Bash(dd *)
Bash(mkfs *)
Bash(curl * | bash)
Bash(wget * | bash)
Bash(git push * --force)
```

See `references/security_patterns.json` for complete safety rules.

### 6. Configuration Backup and Validation

**Before modifying permissions:**
1. Create timestamped backup of settings file
2. Validate permission rule syntax
3. Check for conflicts between allow/deny rules
4. Apply changes
5. Confirm success

**Backup Location:**
```
~/.claude/settings.YYYYMMDD_HHMMSS.backup
.claude/settings.YYYYMMDD_HHMMSS.backup
```

## Workflow: Processing Permission Requests

### Step 1: Detect User Intent

Analyze the user's request to determine what they want to enable:

**Intent Categories:**
- CLI tool (read-only, write, or full access)
- File patterns (specific extension or directory)
- Project type setup
- Permission profile (read-only, development, CI/CD, production)

**Example Intents:**
- "enable git" → CLI tool, read-only preference
- "enable git pushes" → CLI tool, write operations
- "make Rust files editable" → File patterns + project type
- "this is a TypeScript project" → Project type setup
- "enable gcloud list commands" → CLI tool, read-only, specific verb

### Step 2: Determine Required Permissions

Based on detected intent, determine specific permissions to add:

**For CLI Tools:**
1. Check if tool exists in `references/cli_commands.json`
2. If found, extract read-only or write commands based on request
3. If not found, trigger research mode (use Perplexity/Brave/Context7)
4. Format as Bash permission rules: `Bash(git status)`, `Bash(git log)`, etc.

**For File Patterns:**
1. Convert user request to glob patterns
2. Add Read, Write, and Edit permissions as appropriate
3. Example: "markdown files" → `Write(**.md)`, `Edit(**.md)`, `Read(**.md)`

**For Project Types:**
1. Auto-detect or confirm project type
2. Load template from `references/project_templates.json`
3. Merge file patterns and CLI commands from template

### Step 3: Apply Safety Rules

Automatically add deny rules from `references/security_patterns.json`:

```json
{
  "deny": [
    "Read(.env*)",
    "Read(*.key)",
    "Read(*.pem)",
    "Read(.aws/**)",
    "Read(.ssh/**)",
    "Write(.env*)",
    "Bash(rm *)",
    "Bash(sudo *)",
    "Bash(git push * --force)"
  ]
}
```

These rules are ALWAYS included to prevent accidental exposure or destruction.

### Step 4: Execute Permission Update

Use `scripts/apply_permissions.py` to:

1. **Backup Current Settings:**
   ```python
   backup_path = create_backup(settings_path)
   # Creates: ~/.claude/settings.20250116_143022.backup
   ```

2. **Read Current Configuration:**
   ```python
   settings = read_settings(settings_path)
   # Handles: ~/.claude/settings.json or .claude/settings.json
   ```

3. **Merge New Permissions:**
   ```python
   settings['permissions']['allowedTools'].extend(new_permissions)
   settings['permissions']['deny'].extend(safety_rules)
   # Removes duplicates, preserves existing rules
   ```

4. **Validate Configuration:**
   ```python
   validate_permission_syntax(settings)
   check_for_conflicts(settings)
   # Ensures valid tool names, glob patterns, no conflicts
   ```

5. **Write Updated Configuration:**
   ```python
   write_settings(settings_path, settings)
   # Formatted with 2-space indentation
   ```

6. **Confirm Success:**
   ```
   ✅ Permissions updated successfully
   📁 Backup created: ~/.claude/settings.20250116_143022.backup
   🔧 Added 8 new permission rules
   🛡️ Applied 12 safety deny rules
   ```

### Step 5: Inform User

Provide clear feedback about what was changed:

```
✅ Git read-only permissions enabled:
   - Bash(git status)
   - Bash(git log)
   - Bash(git diff)
   - Bash(git show)
   - Bash(git branch)
   - Bash(git remote)

🛡️ Safety rules applied:
   - Denying: Bash(git push * --force)
   - Denying: Read(.env*)
   - Denying: Read(*.key)

💾 Backup saved to: ~/.claude/settings.20250116_143022.backup

Note: Restart Claude Code for changes to take effect.
```

## Example Usage Scenarios

### Scenario 1: Enable Git Read-Only Commands

**User Request:** "enable git"

**Claude Actions:**
1. Detects CLI tool: git
2. Infers read-only preference (no "push", "commit" keywords)
3. Loads git read commands from cli_commands.json
4. Applies safety deny rules
5. Updates settings

**Permissions Added:**
```json
{
  "permissions": {
    "allowedTools": [
      "Bash(git status)",
      "Bash(git log)",
      "Bash(git diff)",
      "Bash(git show)",
      "Bash(git branch)",
      "Bash(git remote)"
    ],
    "deny": [
      "Bash(git push * --force)",
      "Bash(git reset --hard)"
    ]
  }
}
```

### Scenario 2: Enable Git Write Operations

**User Request:** "enable git commits and pushes"

**Claude Actions:**
1. Detects CLI tool: git
2. Identifies write operations requested
3. Adds both read and write git commands
4. Includes extra safety deny rules for dangerous operations

**Permissions Added:**
```json
{
  "permissions": {
    "allowedTools": [
      "Bash(git status)",
      "Bash(git log)",
      "Bash(git diff)",
      "Bash(git commit)",
      "Bash(git push)",
      "Bash(git pull)",
      "Bash(git add)",
      "Bash(git merge)"
    ],
    "deny": [
      "Bash(git push * --force)",
      "Bash(git reset --hard)",
      "Bash(git clean -fd)"
    ]
  }
}
```

### Scenario 3: Rust Project Setup

**User Request:** "this is a Rust project, make it editable"

**Claude Actions:**
1. Auto-detects Cargo.toml (confirms Rust project)
2. Loads rust template from project_templates.json
3. Applies file patterns + cargo commands
4. Adds safety rules

**Permissions Added:**
```json
{
  "permissions": {
    "allowedTools": [
      "Read",
      "Write(src/**.rs)",
      "Write(Cargo.toml)",
      "Write(**.md)",
      "Edit(**.rs)",
      "Edit(Cargo.toml)",
      "Bash(cargo build)",
      "Bash(cargo test)",
      "Bash(cargo check)",
      "Bash(cargo run)",
      "Bash(cargo clean)"
    ],
    "deny": [
      "Write(target/**)",
      "Write(Cargo.lock)",
      "Bash(cargo publish)",
      "Read(.env*)"
    ]
  }
}
```

### Scenario 4: TypeScript Project Setup

**User Request:** "enable TypeScript editing"

**Claude Actions:**
1. Detects TypeScript mention
2. May auto-detect package.json + tsconfig.json
3. Loads typescript template
4. Applies comprehensive TypeScript permissions

**Permissions Added:**
```json
{
  "permissions": {
    "allowedTools": [
      "Read",
      "Write(src/**.ts)",
      "Write(src/**.tsx)",
      "Write(**.json)",
      "Edit(**.ts)",
      "Edit(**.tsx)",
      "Edit(package.json)",
      "Edit(tsconfig.json)",
      "Bash(npm install)",
      "Bash(npm test)",
      "Bash(npm run *)",
      "Bash(npm list)"
    ],
    "deny": [
      "Write(node_modules/**)",
      "Bash(npm publish)",
      "Read(.env*)"
    ]
  }
}
```

### Scenario 5: Make Markdown Files Editable

**User Request:** "make all markdown files editable"

**Claude Actions:**
1. Detects file pattern request
2. Converts to glob patterns
3. Adds appropriate permissions

**Permissions Added:**
```json
{
  "permissions": {
    "allowedTools": [
      "Read(**.md)",
      "Write(**.md)",
      "Edit(**.md)"
    ]
  }
}
```

### Scenario 6: Unknown Tool Research

**User Request:** "enable terraform read commands"

**Claude Actions:**
1. Checks cli_commands.json → not found
2. Uses Perplexity search: "terraform read-only vs write operations"
3. Parses results:
   - Read: plan, show, validate, state list, state show, output, version
   - Write: apply, destroy, init, import
4. Presents findings to user
5. User confirms
6. Applies permissions

**Perplexity Query Example:**
```
Query: "What are the read-only commands for terraform that don't modify infrastructure?
List them separately from write/destructive commands."

Expected Response:
- Read-only: terraform plan, show, validate, state list, output, version
- Write: terraform apply, destroy, init, import, state mv
```

**Permissions Added (after confirmation):**
```json
{
  "permissions": {
    "allowedTools": [
      "Bash(terraform plan)",
      "Bash(terraform show)",
      "Bash(terraform validate)",
      "Bash(terraform state list)",
      "Bash(terraform state show)",
      "Bash(terraform output)",
      "Bash(terraform version)"
    ],
    "deny": [
      "Bash(terraform apply)",
      "Bash(terraform destroy)"
    ]
  }
}
```

### Scenario 7: GCP Read Commands

**User Request:** "enable gcloud list and describe commands"

**Claude Actions:**
1. Detects gcloud CLI tool
2. Identifies specific verbs: list, describe
3. Applies pattern-based permissions

**Permissions Added:**
```json
{
  "permissions": {
    "allowedTools": [
      "Bash(gcloud * list)",
      "Bash(gcloud * describe)",
      "Bash(gcloud * get-iam-policy)"
    ],
    "deny": [
      "Bash(gcloud * delete)",
      "Bash(gcloud projects delete)"
    ]
  }
}
```

### Scenario 8: Java Maven Project

**User Request:** "set up Java Maven project for editing"

**Claude Actions:**
1. Auto-detects pom.xml
2. Loads java-maven template
3. Applies comprehensive Java + Maven permissions

**Permissions Added:**
```json
{
  "permissions": {
    "allowedTools": [
      "Read",
      "Write(src/**.java)",
      "Write(pom.xml)",
      "Write(**.md)",
      "Edit(**.java)",
      "Edit(pom.xml)",
      "Bash(mvn compile)",
      "Bash(mvn test)",
      "Bash(mvn package)",
      "Bash(mvn clean)",
      "Bash(mvn dependency:tree)"
    ],
    "deny": [
      "Write(target/**)",
      "Bash(mvn deploy)",
      "Bash(mvn install)",
      "Read(.env*)"
    ]
  }
}
```

## Resources

### scripts/

**apply_permissions.py** - Core permission manager that handles:
- Reading Claude Code settings from multiple locations
- Creating timestamped backups before modifications
- Merging new permissions with existing configuration
- Validating permission rule syntax
- Writing updated configuration with proper formatting

**detect_project.py** - Auto-detection logic that:
- Scans current directory for language/framework indicators
- Returns detected project type(s)
- Recommends appropriate permission template
- Handles multi-language projects

**validate_config.py** - Configuration validator that:
- Validates permission rule syntax
- Checks for valid tool names
- Validates glob patterns
- Detects conflicts between allow/deny rules
- Reports potential security issues

### references/

**cli_commands.json** - Comprehensive database of CLI tools with:
- Read-only operations for each tool
- Write operations for each tool
- Dangerous operations requiring extra caution
- Covers 15+ major tools (git, gcloud, aws, kubectl, maven, gradle, npm, pip, docker, terraform, etc.)

**project_templates.json** - Permission templates by project type:
- Rust: file patterns + cargo commands
- Java (Maven): .java files + mvn commands
- Java (Gradle): .java files + gradle commands
- TypeScript: .ts/.tsx files + npm commands
- Python: .py files + pip/pytest commands
- Go: .go files + go commands
- JavaScript: .js/.jsx files + npm commands
- Ruby: .rb files + bundle commands
- PHP: .php files + composer commands

**security_patterns.json** - Universal safety rules:
- Sensitive file patterns to deny
- Dangerous commands to deny
- Production environment protections
- Force operation restrictions

### assets/

**permission_profiles.json** - Pre-built permission profiles:
- **read-only**: Only Read tool, denies all writes
- **development**: Full editing of src/, test/, docs/ + common build tools
- **ci-cd**: Build and test commands only, no deployments
- **production**: Minimal permissions for production environments

Users can request: "apply development profile" or "use read-only profile"

## Configuration File Locations

Claude Code uses a hierarchical configuration system. This skill manages permissions in:

**Priority Order (highest to lowest):**
1. Command-line arguments (session-specific)
2. Enterprise policies (if applicable)
3. `.claude/settings.local.json` (local, git-ignored)
4. `.claude/settings.json` (project, version controlled)
5. `~/.claude/settings.json` (user global)
6. `~/.claude.json` (legacy global)

**Default Behavior:**
- Apply to project settings (`.claude/settings.json`) if in a project
- Otherwise apply to user settings (`~/.claude/settings.json`)
- User can specify location with: "add to global settings" or "add to project settings"

## Advanced Features

### Permission Profiles

Users can request pre-built profiles:

**Commands:**
- "apply read-only profile"
- "use development profile"
- "set up CI/CD permissions"
- "apply production profile"

**Profile Definitions:**
See `assets/permission_profiles.json` for complete profile configurations.

### Scoped File Patterns

Support for directory-specific permissions:

**Examples:**
- "make files in src/ editable" → `Write(src/**)`
- "allow editing docs folder" → `Write(docs/**)`
- "enable TypeScript in src only" → `Write(src/**.ts)`

### Multi-Language Projects

Handle projects with multiple languages:

**Detection Logic:**
1. Scan for all language indicators
2. Identify primary language (most files)
3. Identify secondary languages
4. Apply combined template

**Example:**
```
Detected: TypeScript (primary) + Python (secondary)
Applies: TypeScript template + Python template (merged)
```

### Interactive Confirmation

For potentially risky operations, always confirm with user:

**Triggers Confirmation:**
- Write operations on new tools
- Unknown CLI tools discovered via research
- Broad glob patterns (`./**`)
- Removing existing deny rules

**Example Confirmation:**
```
⚠️  This will add write permissions for git push operations.
   This allows Claude to push code to remote repositories.

   Permissions to add:
   - Bash(git push)
   - Bash(git pull)

   Safety rules will also be added:
   - Deny: Bash(git push * --force)

   Proceed? (y/n)
```

## Best Practices

### When to Use This Skill

**Proactive Triggers:**
- User mentions enabling any CLI tool
- User asks to make files editable
- User describes project type
- User requests permission changes
- New project setup

**Pattern Recognition:**
- "enable [tool]" → CLI tool request
- "make [file-type] editable" → File pattern request
- "this is a [language] project" → Project setup
- "allow [operation]" → Specific permission request
- "configure permissions for [tool]" → Tool-specific setup

### Security Considerations

**Always Apply Deny Rules:**
- Never skip safety deny rules
- Always deny sensitive files (.env, .key, .pem)
- Always deny dangerous commands (rm, sudo, dd)
- Always deny force operations (--force flags)

**Validation Before Application:**
- Validate all permission syntax
- Check for conflicts
- Confirm broad glob patterns with user
- Create backup before modifying

**User Education:**
- Explain what permissions are being added
- Explain why deny rules are important
- Warn about potentially risky operations
- Recommend project-local vs global settings

### Performance Optimization

**Minimize Research:**
- Maintain comprehensive built-in database
- Cache research findings
- Prefer built-in knowledge over web search
- Only research truly unknown tools

**Efficient Application:**
- Batch permission updates
- Avoid redundant rules
- Remove duplicates automatically
- Merge related patterns

## Troubleshooting

### Common Issues

**Issue: Permissions not taking effect**
- Solution: Restart Claude Code after modifying settings
- Check: Ensure correct settings file was modified
- Verify: No typos in permission rules

**Issue: Deny rules being ignored**
- Note: This is a known Claude Code limitation
- Workaround: Use multiple layers of deny rules
- Workaround: Use project-local settings for team enforcement

**Issue: Unknown tool not found**
- Solution: Skill will automatically use web search
- Fallback: Manually specify commands
- Option: Update cli_commands.json for future use

**Issue: Too many permission prompts**
- Solution: Apply broader patterns (e.g., `Bash(git *)`)
- Alternative: Apply full tool access instead of command-by-command

### Debugging

**Check Current Permissions:**
```bash
cat ~/.claude/settings.json | grep -A 20 permissions
cat .claude/settings.json | grep -A 20 permissions
```

**Validate Configuration:**
```bash
python3 scripts/validate_config.py ~/.claude/settings.json
```

**Restore from Backup:**
```bash
cp ~/.claude/settings.20250116_143022.backup ~/.claude/settings.json
```

## Summary

This skill provides intelligent, proactive permission management for Claude Code:

✅ **Natural language understanding** - Just describe what you want enabled
✅ **Built-in knowledge** - Pre-configured for 15+ major CLI tools
✅ **Auto-detection** - Recognizes project types automatically
✅ **Research capability** - Can learn unknown tools via web search
✅ **Safety-first** - Always includes deny rules for sensitive operations
✅ **Backup protection** - Creates backups before any changes
✅ **Validation** - Ensures syntactically correct configurations
✅ **Persistent** - Changes survive Claude Code restarts

**Next Steps After Setup:**
1. Test with: "enable git" or "make markdown files editable"
2. Set up your project: "this is a [language] project"
3. Add custom tools to cli_commands.json as needed
4. Share permission profiles with your team
