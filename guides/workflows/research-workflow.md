# Research Workflow for Unknown Tools

## Token Budget Tracker

**This Workflow**:
- Tier 1 (Metadata): 100 tokens ✅ (already loaded)
- Tier 2 (SKILL.md): 2,250 tokens ✅ (already loaded)
- This guide: ~1,500 tokens
- cli_commands.json metadata: ~150 tokens (research instructions)
- MCP tool usage: ~500 tokens (API calls)
- **Estimated total**: 4,500 tokens
- **Status**: ✅ Within budget (<10,000)

---

## Purpose

Research and configure permissions for CLI tools NOT in the pre-configured database:
- "enable perl"
- "allow flutter commands"
- "configure elixir build tools"
- "setup zig compiler permissions"

**When triggered**: After cli-tool-workflow detects unknown tool

---

## Research Tool Priority

**From cli_commands.json `_meta.research_instructions`**:

```json
{
  "priority_order": [
    "mcp__perplexity-ask__perplexity_ask",
    "mcp__brave-search__brave_web_search",
    "Skill(gemini)",
    "WebSearch"
  ]
}
```

**Waterfall Strategy**:
1. Try Perplexity (preferred, most accurate)
2. If fails → Try Brave Search
3. If fails → Try Gemini skill (if available)
4. If fails → Fallback to WebSearch
5. If all fail → Ask user for manual input

---

## Prerequisites

**This workflow triggered when**:
- cli-tool-workflow.md detected unknown tool (grep returned empty)
- User mentions tool not in cli_commands.json database
- Context passed from cli-tool-workflow: `{tool: "perl", mode: "READ"}`

---

## Workflow Steps

### Step 1: Load Research Instructions

**Extract research config from cli_commands.json**:

```bash
jq '._meta.research_instructions' references/cli_commands.json
```

**Token Cost**: ~150 tokens

**Output**:
```json
{
  "priority_order": [...],
  "query_template": "What are the safe read-only commands for {tool}? What are the write/modify commands? What commands should never be allowed (dangerous)?",
  "expected_format": {
    "read_only": ["list of safe commands"],
    "write": ["list of modification commands"],
    "dangerous": ["list of dangerous commands"]
  }
}
```

**Token Cost**: ~150 tokens (surgical extraction)

---

### Step 2: Construct Research Query

**Query Template** (from research_instructions):

```
Tool: {TOOL_NAME}
Mode: {MODE}

Research Questions:
1. What are the safe read-only commands for {TOOL_NAME}?
   (Commands that only display information, no modifications)

2. What are the write/modify commands for {TOOL_NAME}?
   (Commands that change state, write files, or modify configuration)

3. What are dangerous commands for {TOOL_NAME} that should NEVER be allowed?
   (Commands that delete data, force operations, or have security implications)

4. What file patterns does {TOOL_NAME} typically work with?
   (Config files, source files, build outputs)

Format response as JSON:
{
  "tool": "TOOL_NAME",
  "read_only": ["cmd1", "cmd2"],
  "write": ["cmd3", "cmd4"],
  "dangerous": ["cmd5", "cmd6"],
  "file_patterns": {
    "allow": ["pattern1", "pattern2"],
    "deny": ["pattern3"]
  }
}
```

**Example for Perl**:
```
Tool: perl
Mode: READ

Research Questions:
1. What are the safe read-only commands for perl?
2. What are the write/modify commands for perl?
3. What are dangerous commands for perl that should NEVER be allowed?
4. What file patterns does perl typically work with?
```

**Token Cost**: 0 tokens (template construction)

---

### Step 3: Execute Research (Priority Waterfall)

**Step 3a: Try Perplexity (Priority 1)**

```python
mcp__perplexity-ask__perplexity_ask({
  "messages": [
    {
      "role": "user",
      "content": "<constructed_query from Step 2>"
    }
  ]
})
```

**Token Cost**: ~300 tokens (API call + response)

**Expected Response** (Perplexity):
```json
{
  "tool": "perl",
  "read_only": ["perl -v", "perl -c script.pl", "perldoc", "perl -e 'print'"],
  "write": ["perl -pi.bak -e", "perl script.pl > output"],
  "dangerous": ["perl -e 'unlink'", "perl -e 'system(\"rm\")'"],
  "file_patterns": {
    "allow": ["**.pl", "**.pm"],
    "deny": []
  }
}
```

**Success**: Proceed to Step 4
**Failure** (timeout, error, no data): Proceed to Step 3b

---

**Step 3b: Try Brave Search (Priority 2)**

```python
mcp__brave-search__brave_web_search({
  "query": "perl safe read-only commands vs dangerous commands security best practices",
  "count": 5
})
```

**Token Cost**: ~200 tokens (API call + response)

**Success**: Parse results, extract command info
**Failure**: Proceed to Step 3c

---

**Step 3c: Try Gemini Skill (Priority 3)**

**Check if gemini skill available**:
```
IF Skill(gemini) available:
  Invoke Skill(gemini) with research query
ELSE:
  Skip to Step 3d
```

**Token Cost**: ~400 tokens (skill invocation)

**Success**: Extract commands from Gemini response
**Failure**: Proceed to Step 3d

---

**Step 3d: Fallback to WebSearch (Priority 4)**

```python
WebSearch({
  "query": "perl commands list read-only vs write dangerous security"
})
```

**Token Cost**: ~300 tokens

**Success**: Parse search results
**Failure**: Proceed to Step 3e

---

**Step 3e: Manual User Input (Last Resort)**

**If all research methods fail**:

```markdown
❌ **Could not auto-research Perl commands**

I tried:
- ✗ Perplexity API (not available or failed)
- ✗ Brave Search (no results)
- ✗ Gemini skill (not available)
- ✗ Web Search (insufficient data)

**Manual Input Required**:

Please provide Perl commands you want to allow:
1. Read-only commands (safe): ___________
2. Write commands (modify files): ___________
3. Dangerous commands to deny: ___________

Or respond "skip" to cancel Perl setup.
```

**Wait for user input**

**Token Cost**: 0 tokens (user interaction)

---

### Step 4: Parse and Validate Research Results

**Parse response into structured data**:

```json
{
  "tool": "perl",
  "read_only": ["perl -v", "perl -c", "perldoc"],
  "write": ["perl script.pl", "perl -pi.bak"],
  "dangerous": ["perl -e 'unlink'", "perl -e 'system'"],
  "file_patterns": {
    "allow": ["**.pl", "**.pm"],
    "deny": []
  }
}
```

**Validation checks**:
1. ✅ Tool name matches requested tool
2. ✅ At least 1 read_only command OR 1 write command
3. ✅ dangerous array exists (even if empty)
4. ✅ file_patterns has allow array

**If validation fails**:
- Log warning
- Use partial data if available
- Inform user of limitations

**Token Cost**: 0 tokens (validation logic)

---

### Step 5: Build Permission Rules from Research

**Mode-based rule construction**:

**For READ mode** (user requested read-only):
```
Allow Rules:
- Bash(perl -v *)
- Bash(perl -c *)
- Bash(perldoc *)
- Read(**.pl)
- Read(**.pm)

Deny Rules:
- Bash(perl -e 'unlink' *)
- Bash(perl -e 'system' *)
- Bash(perl -pi.bak *)  ← Write command (user requested read-only)
```

**For WRITE mode** (user requested write access):
```
Allow Rules:
- Bash(perl -v *)          ← read_only
- Bash(perl -c *)          ← read_only
- Bash(perl script.pl *)   ← write
- Bash(perl -pi.bak *)     ← write
- Edit(**.pl)
- Edit(**.pm)
- Read(**.pl)
- Read(**.pm)

Deny Rules:
- Bash(perl -e 'unlink' *)  ← dangerous
- Bash(perl -e 'system' *)  ← dangerous
```

**Rule Count**: Typically 8-15 rules per unknown tool

**Token Cost**: 0 tokens (rule generation)

---

### Step 6: Apply Universal Safety Rules

**Load security_patterns.json**:

```bash
jq '.recommended_deny_set.standard' references/security_patterns.json
```

**Token Cost**: ~100 tokens

**Add to deny rules**:
```
- Read(.env*)
- Write(*.key)
- Bash(rm *)
- Bash(sudo *)
... (13 standard deny rules)
```

**Merge with tool-specific dangerous commands**

**Token Cost**: ~100 tokens (security patterns)

---

### Step 7: Execute apply_permissions.py

**Command**:
```bash
python3 scripts/apply_permissions.py \
  --allow "Bash(perl -v *)" \
  --allow "Bash(perl -c *)" \
  --allow "Bash(perldoc *)" \
  --allow "Read(**.pl)" \
  --allow "Read(**.pm)" \
  --deny "Bash(perl -e 'unlink' *)" \
  --deny "Bash(perl -e 'system' *)" \
  --deny "Bash(rm *)" \
  --deny "Bash(sudo *)"
```

**Script Actions**:
1. ✅ Create backup
2. ✅ Validate rules
3. ✅ Merge with settings
4. ✅ Write settings.json
5. ✅ Report

**Token Cost**: 0 tokens (script execution)

---

### Step 8: Offer to Add to Database

**Prompt user**:

```markdown
✅ **Perl permissions configured** (via research)

Would you like me to add Perl to the known tools database?

If yes:
- Future "enable perl" requests will be instant
- Commands saved to references/cli_commands.json
- No research needed next time

**Add Perl to database? (yes/no)**
```

**If user says yes**:

**Step 8a: Update cli_commands.json**

```bash
jq '.perl = {
  "description": "Perl scripting language",
  "read_only": ["perl -v", "perl -c", "perldoc"],
  "write": ["perl script.pl", "perl -pi.bak"],
  "dangerous": ["perl -e '\''unlink'\''", "perl -e '\''system'\''"],
  "file_patterns": {
    "allow": ["**.pl", "**.pm"],
    "deny": []
  }
}' references/cli_commands.json > references/cli_commands.json.tmp \
  && mv references/cli_commands.json.tmp references/cli_commands.json
```

**Step 8b: Commit update** (optional):

```bash
git add references/cli_commands.json
git commit -m "Add Perl tool configuration from research"
```

**Inform user**:
```
✅ Perl added to database. Next time, "enable perl" will be instant!
```

**If user says no**:
- Skip database update
- Permissions still applied (just for this session)

**Token Cost**: 0 tokens (file write, git ops)

---

### Step 9: Confirm with User

**Report Format**:

```markdown
✅ **Perl permissions configured** (researched via Perplexity)

**Commands enabled** (read-only mode):
- ✅ `perl -v` - Version check
- ✅ `perl -c script.pl` - Syntax check
- ✅ `perldoc` - Documentation viewer

**File patterns**:
- ✅ `Read(**.pl)` - Perl scripts
- ✅ `Read(**.pm)` - Perl modules

**Blocked commands** (dangerous):
- 🛡️ `perl -e 'unlink'` - File deletion
- 🛡️ `perl -e 'system'` - System command execution
- 🛡️ `perl -pi.bak` - In-place editing (write mode required)

**Research source**: Perplexity API
**Total rules**: 5 allow, 3 deny

**Backup created**: settings.20250116_155820.backup

**Next step**: Restart Claude Code for changes to take effect.
```

**Token Cost**: 0 tokens (output to user)

---

## Examples

### Example 1: Research Perl (Success via Perplexity)

**User Request**: "enable perl"

**Workflow Execution**:
1. cli-tool-workflow detects unknown → Routes to research-workflow
2. Load research instructions from cli_commands.json._meta
3. Construct query for Perl
4. **Try Perplexity**: SUCCESS
   ```json
   {
     "tool": "perl",
     "read_only": ["perl -v", "perl -c", "perldoc"],
     "write": ["perl script.pl"],
     "dangerous": ["perl -e 'unlink'"]
   }
   ```
5. Build rules (mode=READ): 3 allow, 1 deny
6. Apply safety rules: +13 deny
7. Execute apply_permissions.py
8. Offer to add to database → User says "yes"
9. Update cli_commands.json with Perl entry
10. Confirm with user

**Total tokens**: 4,300 ✅

**Research source**: Perplexity (Priority 1)

---

### Example 2: Research Flutter (Fallback to Brave)

**User Request**: "enable flutter"

**Workflow Execution**:
1. Route from cli-tool-workflow (flutter unknown)
2. Construct query for Flutter
3. **Try Perplexity**: FAILED (timeout)
4. **Try Brave Search**: SUCCESS
   - Search results mention: flutter run, flutter build, flutter test
   - Parse results into structured format
5. Build rules (mode=READ):
   ```
   Allow: Bash(flutter doctor *), Bash(flutter --version *)
   Deny: Bash(flutter build *), Bash(flutter pub publish *)
   ```
6. Apply safety rules
7. Execute apply_permissions.py
8. Offer to add to database → User says "no" (wants to test first)
9. Confirm with user

**Total tokens**: 4,400 ✅

**Research source**: Brave Search (Priority 2 fallback)

---

### Example 3: Research Zig (Manual Input Required)

**User Request**: "enable zig compiler"

**Workflow Execution**:
1. Route from cli-tool-workflow (zig unknown)
2. Construct query for Zig
3. **Try Perplexity**: FAILED (no Zig data)
4. **Try Brave**: FAILED (insufficient results)
5. **Try Gemini skill**: NOT AVAILABLE
6. **Try WebSearch**: FAILED (unclear results)
7. **Manual input**: Ask user for Zig commands
   ```
   User provides:
   - Read-only: zig version, zig targets
   - Write: zig build, zig test
   - Dangerous: zig build install (system-wide install)
   ```
8. Build rules from user input
9. Apply safety rules
10. Execute apply_permissions.py
11. Offer to add to database → User says "yes"
12. Update cli_commands.json with Zig entry (from user input)
13. Confirm with user

**Total tokens**: 4,500 ✅

**Research source**: Manual user input (Priority 5 fallback)

---

### Example 4: Research Unknown Tool with Write Mode

**User Request**: "enable elixir with write access"

**Workflow Execution**:
1. Tool=elixir, Mode=WRITE
2. Construct query for Elixir
3. **Try Perplexity**: SUCCESS
   ```json
   {
     "tool": "elixir",
     "read_only": ["elixir --version", "iex", "mix help"],
     "write": ["mix compile", "mix test", "mix run"],
     "dangerous": ["mix release --overwrite", "mix ecto.drop"]
   }
   ```
4. Build rules for WRITE mode:
   ```
   Allow:
   - Bash(elixir --version *)  ← read_only
   - Bash(mix help *)          ← read_only
   - Bash(mix compile *)       ← write
   - Bash(mix test *)          ← write
   - Edit(**.ex)               ← Elixir source files
   - Edit(**.exs)              ← Elixir scripts
   - Read(**.ex), Read(**.exs)

   Deny:
   - Bash(mix release --overwrite *)  ← dangerous
   - Bash(mix ecto.drop *)            ← dangerous (drops database)
   ```
5. Apply safety rules
6. Execute apply_permissions.py (12 allow, 15 deny)
7. Offer to add to database → User says "yes"
8. Confirm with comprehensive report

**Total tokens**: 4,400 ✅

---

## Error Handling

### Error 1: All research methods fail

**Detection**: All 4 priorities return no data + user declines manual input

**Example**:
```
Perplexity: timeout
Brave: no results
Gemini: not available
WebSearch: insufficient data
User: "skip" (declines manual input)
```

**Action**:
1. Inform: "Cannot configure obscure-tool without command information"
2. Suggest alternatives:
   - "Provide commands manually later"
   - "Add tool to cli_commands.json yourself (see references/cli_commands.json format)"
   - "Use file-pattern-workflow to enable file editing only"
3. Exit workflow without applying permissions

**Recovery**: Manual database entry or skip tool

---

### Error 2: Research returns malformed data

**Detection**: Response doesn't match expected JSON format

**Example**:
```json
{
  "commands": "perl has many commands"  ← Not structured
}
```

**Action**:
1. Log: "Research returned malformed data for perl"
2. Attempt to parse natural language response:
   - Extract commands using regex
   - Look for patterns like "safe commands: X, Y, Z"
3. If parsing succeeds: Proceed with partial data
4. If parsing fails: Fallback to next priority or manual input

**Recovery**: Best-effort parsing or fallback

---

### Error 3: Research contradicts user's mode request

**Detection**: User requested READ but research shows tool is write-only

**Example**:
```
User: "enable make read-only"
Research: "make is a build tool, inherently modifies files"
```

**Action**:
1. **WARN user**: "make is a build tool and requires write access to function"
2. **ASK**: "Enable make with write permissions anyway? (yes/no)"
3. If yes: Apply write mode despite READ request
4. If no: Cancel make setup

**Safety principle**: Inform user when tool can't operate in requested mode

---

### Error 4: Database update fails (Step 8)

**Detection**: jq update or git commit fails

**Example Error**:
```
❌ Failed to update cli_commands.json: Permission denied
```

**Action**:
1. Permissions STILL applied (user can use tool immediately)
2. **INFORM**: "Perl permissions applied but couldn't add to database"
3. **SUGGEST**: "Manually add to references/cli_commands.json or fix file permissions"
4. Exit workflow (permissions already applied in Step 7)

**Recovery**: Manual database entry later (not critical for immediate use)

---

## Edge Cases

### Edge Case 1: Tool already partially known

**Example**: Database has "perl" with only 2 commands, research finds 10 more

**Handling**:
1. Detect: Tool exists in database but incomplete
2. **ASK user**: "Perl is in database but research found more commands. Update entry? (yes/no)"
3. If yes:
   - Merge research results with existing entry
   - Keep user customizations if any
   - Update database
4. If no:
   - Use existing database entry only

**Policy**: User can choose to expand existing entries

---

### Edge Case 2: Research suggests file patterns not requested

**Example**: User asked for "enable perl" (just commands), research suggests **.pl editing

**Handling**:
1. Research returns file_patterns in addition to commands
2. **INFORM user**: "Research suggests editing **.pl files. Enable file editing too? (yes/no)"
3. If yes: Add Edit(**.pl) + Read(**.pl) rules
4. If no: Skip file patterns, apply only command rules

**Default**: Ask user (don't assume file editing wanted)

---

### Edge Case 3: Tool has aliases

**Example**: Research finds "python" and "python3" are same tool

**Handling**:
1. Research returns: `"aliases": ["python", "python3"]`
2. Apply rules for BOTH aliases:
   ```
   Bash(python *)
   Bash(python3 *)
   ```
3. Inform: "Enabled python (including python3 alias)"

**Token cost**: Minimal (just extra rules)

---

### Edge Case 4: Research quality varies by priority

**Example**:
- Perplexity: Detailed with 10 commands + examples
- Brave: Generic with 3 commands only
- WebSearch: Vague with unclear safety info

**Handling**:
1. **Prefer higher priority** even if less commands (more trustworthy)
2. **Exception**: If higher priority < 3 commands AND lower priority >= 5 commands
   - Consider using lower priority with warning
   - **ASK user**: "Perplexity found 2 commands, Brave found 7. Use Brave results? (yes/no)"

**Safety first**: Prefer authoritative source even if less comprehensive

---

## Success Criteria

**Workflow complete when**:
- ✅ Unknown tool researched via priority waterfall
- ✅ Command structure extracted (read_only, write, dangerous)
- ✅ Mode-appropriate rules built
- ✅ Universal safety rules applied
- ✅ Backup created
- ✅ Validation passed
- ✅ settings.json written
- ✅ (Optional) Database updated with new tool
- ✅ User informed with research source
- ✅ Restart reminder provided

---

## Token Budget Summary

**Successful research (Perplexity)**:
```
Tier 1 (Metadata):          100 tokens ✅
Tier 2 (SKILL.md):        2,250 tokens ✅
research-workflow.md:     1,500 tokens (this file)
cli_commands metadata:      150 tokens (research config)
Perplexity API:             300 tokens (query + response)
Security patterns:          100 tokens (surgical)
---
Total:                    4,400 tokens
Status:                   ✅ 56% under budget
```

**Research with fallbacks (Brave)**:
```
Tier 1 + 2 + this:        3,850 tokens ✅
Perplexity attempt:         100 tokens (failed)
Brave API:                  200 tokens (success)
Security patterns:          100 tokens
---
Total:                    4,250 tokens
Status:                   ✅ 57% under budget
```

**Manual input (all research failed)**:
```
Tier 1 + 2 + this:        3,850 tokens ✅
All research attempts:      600 tokens (all failed)
User interaction:             0 tokens
Security patterns:          100 tokens
---
Total:                    4,550 tokens
Status:                   ✅ 54% under budget
```

---

## Next Steps After Workflow

**User must restart Claude Code** for permissions to take effect.

**Testing the researched tool**:
1. Try a read-only command (should work)
2. Try a write command if mode=WRITE (should work)
3. Try a dangerous command (should be blocked)

**If tool doesn't work as expected**:
- Research may have been incomplete
- User can add missing commands via cli-tool-workflow
- Or manually edit cli_commands.json

**Optional follow-ups**:
- Validate: `python3 scripts/validate_config.py`
- View what was researched: `jq '.TOOL_NAME' references/cli_commands.json` (if added to database)
- Share with community: Contribute researched tool to upstream repo

---

**End of Research Workflow**
**Size**: ~600 lines (~3,000 tokens)
**Compliance**: ✅ Tier 3 (loaded on-demand only)
