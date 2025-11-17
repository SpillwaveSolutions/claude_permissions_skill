# Backup and Restore Workflow

## Token Budget Tracker

**This Workflow**:
- Tier 1 (Metadata): 100 tokens ✅ (already loaded)
- Tier 2 (SKILL.md): 2,250 tokens ✅ (already loaded)
- This guide: ~600 tokens
- Script execution: 0 tokens
- **Estimated total**: 2,950 tokens
- **Status**: ✅ Within budget (<10,000)

---

## Purpose

Manage permission backups and restore previous configurations:
- "show available backups"
- "restore previous permissions"
- "rollback last change"
- "undo profile application"

**When triggered**: User requests backup/restore OR after catastrophic validation failure

---

## Backup System

**Automatic backups** created by apply_permissions.py:
- Format: `settings.YYYYMMDD_HHMMSS.backup`
- Location: Same directory as settings.json
- Created: Before every permission modification
- Retention: Unlimited (user manages cleanup)

**Example backups**:
```
settings.20250116_153045.backup  ← 2 hours ago (development profile)
settings.20250116_120122.backup  ← 5 hours ago (added git permissions)
settings.20250115_180934.backup  ← Yesterday (project setup)
settings.20250114_163420.backup  ← 2 days ago (initial config)
```

---

## Workflow Steps

### Step 1: List Available Backups

**Command**:
```bash
ls -lt ~/.config/claude-code/settings.*.backup | head -10
```

**Example Output**:
```
-rw-r--r--  1 user  staff  4521 Jan 16 15:30 settings.20250116_153045.backup
-rw-r--r--  1 user  staff  3812 Jan 16 12:01 settings.20250116_120122.backup
-rw-r--r--  1 user  staff  2945 Jan 15 18:09 settings.20250115_180934.backup
-rw-r--r--  1 user  staff  1204 Jan 14 16:34 settings.20250114_163420.backup
```

**Parse and present to user**:

```markdown
## Available Backups

| # | Timestamp | Age | Size | Description |
|---|-----------|-----|------|-------------|
| 1 | 2025-01-16 15:30 | 2 hours ago | 4.5KB | Most recent (development profile) |
| 2 | 2025-01-16 12:01 | 5 hours ago | 3.8KB | Before adding git permissions |
| 3 | 2025-01-15 18:09 | Yesterday | 2.9KB | Project setup (Rust template) |
| 4 | 2025-01-14 16:34 | 2 days ago | 1.2KB | Initial configuration |

**Which backup to restore? (1-4, or 'cancel')**
```

**Token Cost**: 0 tokens (ls command + formatting)

---

### Step 2: User Selects Backup

**Parse user response**:
- Number (1-4): Restore specific backup
- "cancel" / "none": Exit without restoring
- "latest" / "most recent": Restore #1
- "previous" / "last": Restore #2

**If user selects backup #2**:
- Backup file: `settings.20250116_120122.backup`
- Description: "Before adding git permissions"

**Token Cost**: 0 tokens (user interaction)

---

### Step 3: Show Restore Preview

**Before restoring, show what will change**:

```bash
# Compare current settings with selected backup
diff settings.json settings.20250116_120122.backup
```

**Present diff to user**:

```markdown
## Restore Preview

**Restoring**: Backup from 2025-01-16 12:01 (5 hours ago)
**Description**: Before adding git permissions

**Changes** (current → backup):

**Will be REMOVED** (added since backup):
- ✗ Bash(git status *)
- ✗ Bash(git log *)
- ✗ Bash(git diff *)
- ✗ Read(**.rs)

**Will be RESTORED** (removed since backup):
- ✓ Edit(docs/*.md)  ← Was removed
- ✓ Bash(cargo test *)  ← Was removed

**Net change**: -4 rules (current: 45 → backup: 41)

**Proceed with restore? (yes/no)**
```

**Token Cost**: 0 tokens (diff command + formatting)

---

### Step 4: Confirm Restore

**If user says "yes"**:
- Proceed to Step 5 (execute restore)

**If user says "no"**:
```markdown
❌ Restore cancelled

Current permissions unchanged.

Options:
- Select different backup (run workflow again)
- View current permissions: `cat settings.json`
- Validate current: see validation-workflow.md
```

**Token Cost**: 0 tokens (user interaction)

---

### Step 5: Execute Restore

**Create safety backup of CURRENT state**:
```bash
cp settings.json settings.pre-restore-$(date +%Y%m%d_%H%M%S).backup
```

**Restore selected backup**:
```bash
cp settings.20250116_120122.backup settings.json
```

**Validate restored settings**:
```bash
python3 scripts/validate_config.py
```

**Expected Output**:
```
✅ Safety backup created: settings.pre-restore-20250116_173045.backup
✅ Restored from: settings.20250116_120122.backup
✅ Validation passed: Restored settings are valid
✅ Settings written to: settings.json

Summary:
  Restored from: 2025-01-16 12:01 (5 hours ago)
  Total allow rules: 38 (-7 from current)
  Total deny rules: 13 (+2 from current)
  Validation status: ✅ VALID
```

**If validation FAILS**:
```
❌ Restored backup failed validation!

Issues found:
- 2 syntax errors
- 1 security vulnerability

**Recommendation**: Restore different backup or revert to pre-restore state

**Revert to pre-restore state? (yes/no)**
```

**Token Cost**: 0 tokens (script execution)

---

### Step 6: Confirm with User

**Report Format** (successful restore):

```markdown
✅ **Permissions restored successfully**

**Restored from**: 2025-01-16 12:01 (5 hours ago)
**Description**: Before adding git permissions

**Changes applied**:
- ✗ Removed 7 rules (added since backup)
- ✓ Restored 2 rules (that were removed)

**Current state**:
- Total allow rules: 38
- Total deny rules: 13
- Validation: ✅ PASSED
- Security score: 90/100

**Safety net**: Pre-restore state backed up to:
- `settings.pre-restore-20250116_173045.backup`
- Can undo this restore if needed

**Next step**: Restart Claude Code for restored permissions to take effect.
```

**Token Cost**: 0 tokens (output to user)

---

## Examples

### Example 1: Undo Recent Profile Application

**User Request**: "restore previous permissions" (just applied development profile, too broad)

**Workflow Execution**:
1. List backups:
   ```
   1. settings.20250116_170012.backup (5 min ago - development profile)
   2. settings.20250116_153045.backup (2 hours ago - custom config)
   ```
2. User wants to undo development profile → Select #2
3. Show preview:
   ```
   Will remove: 68 rules from development profile
   Will restore: 15 custom rules
   ```
4. User confirms: "yes"
5. Execute:
   - Safety backup current (development profile) → settings.pre-restore-*.backup
   - Restore settings.20250116_153045.backup
   - Validate: ✅ PASSED
6. Confirm: "Restored custom config. Development profile undone."

**Total tokens**: 2,950 ✅

---

### Example 2: Recover from Validation Failure

**User Request**: "validation failed, restore backup"

**Workflow Execution**:
1. Triggered by validation-workflow (too many errors)
2. List backups (most recent 3)
3. Recommend most recent valid backup:
   ```
   Recommended: #1 (settings.20250116_153045.backup)
   Reason: Last known good state
   ```
4. User accepts recommendation
5. Show preview (current is INVALID, backup is VALID)
6. Execute restore
7. Validate: ✅ PASSED
8. Confirm: "Recovered from validation failure. Settings now valid."

**Total tokens**: 2,950 ✅

**Use case**: Emergency recovery

---

### Example 3: Rollback Last Change

**User Request**: "rollback last change"

**Workflow Execution**:
1. Interpret "last change" as most recent backup
2. Auto-select backup #1 (most recent)
3. Show preview of what will be undone
4. User confirms
5. Execute restore
6. Confirm: "Last change rolled back"

**Total tokens**: 2,950 ✅

**Shortcut**: "rollback" = restore most recent backup

---

### Example 4: Compare Multiple Backups

**User Request**: "show me what changed between backups"

**Workflow Execution**:
1. List backups
2. User says "compare 1 and 3"
3. Run diff:
   ```bash
   diff settings.20250116_153045.backup settings.20250115_180934.backup
   ```
4. Show differences:
   ```
   Between backup #1 and #3 (yesterday):
   - Added 23 rules (git, docker, npm)
   - Removed 2 rules (outdated patterns)
   - Net: +21 rules
   ```
5. User can choose to restore either one

**Total tokens**: 2,950 ✅

**Use case**: Understanding permission evolution

---

## Error Handling

### Error 1: No backups found

**Detection**: ls command returns empty

**Action**:
```markdown
❌ **No backups found**

Location checked: ~/.config/claude-code/
Pattern: settings.*.backup

**Possible causes**:
1. First time using skill (no backups created yet)
2. Backups deleted/moved
3. Wrong settings.json location

**Recommendation**:
- Current settings have no backup safety net
- Create manual backup: `cp settings.json settings.manual-$(date +%Y%m%d_%H%M%S).backup`
- Future permission changes will auto-create backups
```

**Recovery**: Create manual backup going forward

---

### Error 2: Restored backup fails validation

**Detection**: validate_config.py reports errors after restore

**Example**:
```
❌ Restored backup has 5 syntax errors
```

**Action**:
```markdown
❌ **Restored backup is invalid**

Backup: settings.20250115_180934.backup
Errors: 5 syntax errors, 1 security issue

**This backup is corrupted or outdated.**

**Options**:
1. Restore different backup (newer/older)
2. Revert to pre-restore state (undo this restore)
3. Fix validation errors manually

**Which option? (1/2/3)**
```

**Recovery**: Try different backup or revert

---

### Error 3: Backup file corrupted

**Detection**: Cannot parse backup file as JSON

**Action**:
```markdown
❌ **Backup file corrupted**

File: settings.20250115_180934.backup
Error: Invalid JSON (cannot parse)

**This backup cannot be restored.**

**Try**:
- Select different backup
- Or restore from oldest backup (likely valid)
- Or manually reconstruct settings.json

**Select different backup? (yes/no)**
```

**Recovery**: Skip corrupted backup, try others

---

### Error 4: Permission denied (cannot write)

**Detection**: cp command fails with permission error

**Action**:
```markdown
❌ **Cannot restore backup**

Error: Permission denied writing to settings.json

**Cause**: File permissions issue

**Fix**:
1. Check file permissions: `ls -l settings.json`
2. If read-only, make writable: `chmod u+w settings.json`
3. Retry restore

Or: Restore manually with sudo (not recommended)
```

**Recovery**: Fix file permissions

---

## Edge Cases

### Edge Case 1: Restore older backup (skip intermediate)

**Example**: Restore backup #4, skipping #2 and #3

**Handling**:
- Allow user to select any backup
- Show preview comparing current vs selected (may show large diff)
- Warn if diff is large (>50 rules):
  ```
  ⚠️  Large change detected: 78 rules different
  This will undo multiple permission changes.
  Are you sure? (yes/no)
  ```

**No restriction**: User can restore any backup

---

### Edge Case 2: Multiple restores in a row

**Example**: User restores backup #2, then immediately restores backup #3

**Handling**:
- Each restore creates pre-restore backup
- User can chain restores indefinitely
- Backup history grows:
  ```
  settings.pre-restore-20250116_173045.backup  ← After 1st restore
  settings.pre-restore-20250116_173212.backup  ← After 2nd restore
  ```

**Recommendation**: Inform user of growing backups, suggest cleanup

---

### Edge Case 3: Restore to settings that require unavailable tools

**Example**: Backup has Perplexity MCP permissions but MCP not installed

**Handling**:
- Restore succeeds (settings are syntactically valid)
- Validation may warn: "mcp__perplexity-ask referenced but not available"
- **Inform user**:
  ```
  ⚠️  Restored settings reference tools not currently available:
  - mcp__perplexity-ask__perplexity_ask

  Settings are valid but these tools won't work until:
  - Install missing MCP servers
  - Or remove references to unavailable tools
  ```

**Not an error**: Settings valid, just some tools unavailable

---

### Edge Case 4: Restore same as current

**Example**: User selects backup identical to current settings

**Handling**:
- Detect via diff (no changes)
- Inform:
  ```
  ℹ️  **No changes needed**

  Selected backup is identical to current settings.
  Restore not necessary.

  Current settings already match backup from 2025-01-16 12:01.
  ```
- Skip restore (no-op)

**Optimization**: Detect no-op restores early

---

## Backup Cleanup

**User may accumulate many backups**:

```markdown
## Backup Cleanup (Optional)

You have 47 backup files (oldest: 2024-12-01)

**Cleanup options**:
1. Keep last 10 backups only
2. Delete backups older than 30 days
3. Keep 1 backup per day (consolidate)
4. Manual selection

**Cleanup? (1-4 or skip)**
```

**If user chooses #2 (delete >30 days)**:
```bash
find ~/.config/claude-code -name "settings.*.backup" -mtime +30 -delete
```

**Inform**:
```
✅ Deleted 38 old backups (kept 9 recent)
```

**Token Cost**: 0 tokens (cleanup optional, not part of core workflow)

---

## Success Criteria

**Workflow complete when**:
- ✅ Available backups listed
- ✅ User selected backup (or cancelled)
- ✅ Restore preview shown
- ✅ User confirmed restore
- ✅ Pre-restore safety backup created
- ✅ Selected backup restored to settings.json
- ✅ Restored settings validated (passed)
- ✅ User informed of restore completion
- ✅ Restart reminder provided

---

## Token Budget Summary

**List backups only** (user cancels):
```
Tier 1 (Metadata):          100 tokens ✅
Tier 2 (SKILL.md):        2,250 tokens ✅
backup-restore-workflow:    600 tokens (this file)
ls command:                   0 tokens (execution)
---
Total:                    2,950 tokens
Status:                   ✅ 70% under budget
```

**Full restore operation**:
```
Tier 1 + 2 + this:        2,950 tokens ✅
diff preview:                 0 tokens (command)
cp restore:                   0 tokens (command)
validate_config.py:           0 tokens (script)
---
Total:                    2,950 tokens
Status:                   ✅ 70% under budget
```

---

## Integration with Other Workflows

**Backup/restore is used BY**:
- validation-workflow (restore after validation failure)
- profile-application-workflow (undo profile if user doesn't like it)
- Any workflow (emergency recovery)

**Backup/restore is**: Universal safety net for all workflows

**Every modification workflow** creates backups via apply_permissions.py

---

## Next Steps After Workflow

**After successful restore**:
- ✅ Restart Claude Code (required)
- ✅ Test that restored permissions work as expected
- ✅ Optional: Validate restored settings (`python3 scripts/validate_config.py`)

**If restore didn't help**:
- Try different backup (older/newer)
- Or manually reconstruct permissions
- Or apply fresh profile (development, read-only, etc.)

**Backup safety net**:
- Pre-restore backup allows undoing the restore
- Can always go back to pre-restore state

---

## Quick Commands Reference

**List recent backups**:
```bash
ls -lt ~/.config/claude-code/settings.*.backup | head -5
```

**Restore specific backup manually**:
```bash
cp settings.YYYYMMDD_HHMMSS.backup settings.json
```

**View backup contents**:
```bash
cat settings.YYYYMMDD_HHMMSS.backup | jq .
```

**Compare two backups**:
```bash
diff settings.BACKUP1.backup settings.BACKUP2.backup
```

**Delete old backups (>30 days)**:
```bash
find ~/.config/claude-code -name "settings.*.backup" -mtime +30 -delete
```

---

**End of Backup/Restore Workflow**
**Size**: ~400 lines (~2,000 tokens)
**Compliance**: ✅ Tier 3 (loaded on-demand only)
