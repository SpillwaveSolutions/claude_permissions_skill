#!/usr/bin/env python3
"""
Permission Manager for Claude Code

Applies, validates, and manages Claude Code permission configurations.
Creates backups before modifications and ensures syntactically correct rules.

Usage:
    apply_permissions.py --add "Bash(git status)" --add "Write(**.md)"
    apply_permissions.py --add-profile development
    apply_permissions.py --validate ~/.claude/settings.json
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
import shutil


class PermissionManager:
    """Manages Claude Code permissions with validation and backup."""

    VALID_TOOLS = {
        'Bash', 'Read', 'Write', 'Edit', 'WebFetch', 'WebSearch',
        'SlashCommand', 'NotebookEdit'
    }

    CONFIG_LOCATIONS = {
        'global_legacy': Path.home() / '.claude.json',
        'global_user': Path.home() / '.claude' / 'settings.json',
        'project': Path.cwd() / '.claude' / 'settings.json',
        'project_local': Path.cwd() / '.claude' / 'settings.local.json'
    }

    def __init__(self):
        self.settings_path: Optional[Path] = None
        self.settings: Dict = {}

    def detect_settings_file(self, prefer_global: bool = False) -> Path:
        """
        Detect which settings file to use based on context.

        Args:
            prefer_global: If True, prefer global settings over project

        Returns:
            Path to the appropriate settings file
        """
        if not prefer_global:
            # Check for project settings first
            if self.CONFIG_LOCATIONS['project'].exists():
                return self.CONFIG_LOCATIONS['project']

        # Check for global user settings
        if self.CONFIG_LOCATIONS['global_user'].exists():
            return self.CONFIG_LOCATIONS['global_user']

        # Check for legacy global settings
        if self.CONFIG_LOCATIONS['global_legacy'].exists():
            return self.CONFIG_LOCATIONS['global_legacy']

        # Default to creating global user settings
        global_user = self.CONFIG_LOCATIONS['global_user']
        global_user.parent.mkdir(parents=True, exist_ok=True)
        return global_user

    def create_backup(self, settings_path: Path) -> Path:
        """
        Create timestamped backup of settings file.

        Args:
            settings_path: Path to settings file

        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = settings_path.with_suffix(f'.{timestamp}.backup')

        if settings_path.exists():
            shutil.copy2(settings_path, backup_path)
            print(f"📁 Backup created: {backup_path}")

        return backup_path

    def read_settings(self, settings_path: Path) -> Dict:
        """
        Read settings from file, creating default structure if not exists.

        Args:
            settings_path: Path to settings file

        Returns:
            Settings dictionary
        """
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                return json.load(f)

        # Create default structure
        return {
            "permissions": {
                "allowedTools": [],
                "deny": []
            }
        }

    def write_settings(self, settings_path: Path, settings: Dict):
        """
        Write settings to file with proper formatting.

        Args:
            settings_path: Path to settings file
            settings: Settings dictionary
        """
        settings_path.parent.mkdir(parents=True, exist_ok=True)

        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)

        print(f"✅ Settings written to: {settings_path}")

    def validate_permission_rule(self, rule: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a permission rule format.

        Args:
            rule: Permission rule string

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if it's just a tool name
        if rule in self.VALID_TOOLS:
            return (True, None)

        # Check if it's Tool(pattern) format
        if '(' not in rule:
            return (False, f"Invalid format: '{rule}'. Expected 'ToolName' or 'ToolName(pattern)'")

        try:
            tool, pattern_part = rule.split('(', 1)

            if tool not in self.VALID_TOOLS:
                return (False, f"Unknown tool: '{tool}'. Valid tools: {', '.join(sorted(self.VALID_TOOLS))}")

            if not pattern_part.endswith(')'):
                return (False, f"Missing closing parenthesis in: '{rule}'")

            return (True, None)

        except Exception as e:
            return (False, f"Parse error in '{rule}': {e}")

    def validate_settings(self, settings: Dict) -> List[str]:
        """
        Validate entire settings configuration.

        Args:
            settings: Settings dictionary

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if 'permissions' not in settings:
            errors.append("Missing 'permissions' key in settings")
            return errors

        permissions = settings['permissions']

        # Validate allowedTools
        if 'allowedTools' in permissions:
            for rule in permissions['allowedTools']:
                is_valid, error = self.validate_permission_rule(rule)
                if not is_valid:
                    errors.append(f"allowedTools: {error}")

        # Validate deny rules
        if 'deny' in permissions:
            for rule in permissions['deny']:
                is_valid, error = self.validate_permission_rule(rule)
                if not is_valid:
                    errors.append(f"deny: {error}")

        return errors

    def merge_permissions(
        self,
        existing: List[str],
        new: List[str],
        remove_duplicates: bool = True
    ) -> List[str]:
        """
        Merge new permissions with existing ones.

        Args:
            existing: Existing permission rules
            new: New permission rules to add
            remove_duplicates: Whether to remove duplicate rules

        Returns:
            Merged list of permissions
        """
        if remove_duplicates:
            # Use set to remove duplicates while preserving order
            seen = set(existing)
            merged = list(existing)

            for rule in new:
                if rule not in seen:
                    merged.append(rule)
                    seen.add(rule)

            return merged
        else:
            return existing + new

    def add_permissions(
        self,
        allow_rules: List[str] = None,
        deny_rules: List[str] = None,
        settings_path: Optional[Path] = None,
        create_backup: bool = True
    ) -> bool:
        """
        Add permissions to settings file.

        Args:
            allow_rules: List of permission rules to allow
            deny_rules: List of permission rules to deny
            settings_path: Path to settings file (auto-detect if None)
            create_backup: Whether to create backup before modifying

        Returns:
            True if successful, False otherwise
        """
        allow_rules = allow_rules or []
        deny_rules = deny_rules or []

        # Detect settings file if not specified
        if settings_path is None:
            settings_path = self.detect_settings_file()

        self.settings_path = settings_path

        # Validate new rules
        all_rules = allow_rules + deny_rules
        for rule in all_rules:
            is_valid, error = self.validate_permission_rule(rule)
            if not is_valid:
                print(f"❌ Validation error: {error}")
                return False

        # Create backup if requested
        if create_backup:
            self.create_backup(settings_path)

        # Read existing settings
        settings = self.read_settings(settings_path)

        # Ensure permissions structure exists
        if 'permissions' not in settings:
            settings['permissions'] = {}
        if 'allowedTools' not in settings['permissions']:
            settings['permissions']['allowedTools'] = []
        if 'deny' not in settings['permissions']:
            settings['permissions']['deny'] = []

        # Merge new permissions
        if allow_rules:
            settings['permissions']['allowedTools'] = self.merge_permissions(
                settings['permissions']['allowedTools'],
                allow_rules
            )

        if deny_rules:
            settings['permissions']['deny'] = self.merge_permissions(
                settings['permissions']['deny'],
                deny_rules
            )

        # Validate complete settings
        errors = self.validate_settings(settings)
        if errors:
            print("❌ Validation errors:")
            for error in errors:
                print(f"   - {error}")
            return False

        # Write settings
        self.write_settings(settings_path, settings)

        # Report what was added
        print(f"\n🔧 Added {len(allow_rules)} allow rule(s)")
        print(f"🛡️  Added {len(deny_rules)} deny rule(s)")

        if allow_rules:
            print("\n✅ Allowed:")
            for rule in allow_rules:
                print(f"   - {rule}")

        if deny_rules:
            print("\n🚫 Denied:")
            for rule in deny_rules:
                print(f"   - {rule}")

        print("\n⚠️  Note: Restart Claude Code for changes to take effect.")

        return True

    def load_profile(self, profile_name: str) -> Tuple[List[str], List[str]]:
        """
        Load permission profile from assets.

        Args:
            profile_name: Name of profile (read-only, development, ci-cd, production)

        Returns:
            Tuple of (allow_rules, deny_rules)
        """
        profiles_path = Path(__file__).parent.parent / 'assets' / 'permission_profiles.json'

        if not profiles_path.exists():
            print(f"❌ Profile file not found: {profiles_path}")
            return ([], [])

        with open(profiles_path, 'r') as f:
            profiles = json.load(f)

        if profile_name not in profiles:
            print(f"❌ Profile '{profile_name}' not found")
            print(f"   Available profiles: {', '.join(profiles.keys())}")
            return ([], [])

        profile = profiles[profile_name]
        return (profile.get('allowedTools', []), profile.get('deny', []))


def main():
    parser = argparse.ArgumentParser(
        description='Manage Claude Code permissions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add specific permissions
  %(prog)s --add "Bash(git status)" --add "Bash(git log)"

  # Add file permissions
  %(prog)s --add "Write(**.md)" --add "Edit(**.md)"

  # Add deny rules
  %(prog)s --deny "Bash(rm *)" --deny "Read(.env*)"

  # Apply a profile
  %(prog)s --profile development

  # Validate settings file
  %(prog)s --validate ~/.claude/settings.json

  # Use global settings instead of project
  %(prog)s --global --add "Read"
        """
    )

    parser.add_argument(
        '--add',
        action='append',
        metavar='RULE',
        help='Add permission rule to allowedTools (can be used multiple times)'
    )

    parser.add_argument(
        '--deny',
        action='append',
        metavar='RULE',
        help='Add permission rule to deny list (can be used multiple times)'
    )

    parser.add_argument(
        '--profile',
        metavar='NAME',
        help='Apply pre-built permission profile (read-only, development, ci-cd, production)'
    )

    parser.add_argument(
        '--settings',
        metavar='PATH',
        type=Path,
        help='Path to settings file (auto-detected if not specified)'
    )

    parser.add_argument(
        '--global',
        dest='use_global',
        action='store_true',
        help='Use global settings instead of project settings'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup before modifying settings'
    )

    parser.add_argument(
        '--validate',
        metavar='FILE',
        type=Path,
        help='Validate settings file without modifying it'
    )

    args = parser.parse_args()

    manager = PermissionManager()

    # Handle validation mode
    if args.validate:
        if not args.validate.exists():
            print(f"❌ File not found: {args.validate}")
            return 1

        settings = manager.read_settings(args.validate)
        errors = manager.validate_settings(settings)

        if errors:
            print(f"❌ Validation failed for {args.validate}:")
            for error in errors:
                print(f"   - {error}")
            return 1
        else:
            print(f"✅ {args.validate} is valid")
            return 0

    # Collect rules to add
    allow_rules = args.add or []
    deny_rules = args.deny or []

    # Handle profile
    if args.profile:
        profile_allow, profile_deny = manager.load_profile(args.profile)
        allow_rules.extend(profile_allow)
        deny_rules.extend(profile_deny)
        print(f"📋 Loaded profile: {args.profile}")

    # Check if anything to do
    if not allow_rules and not deny_rules:
        parser.print_help()
        return 1

    # Determine settings file
    settings_path = args.settings
    if settings_path is None:
        settings_path = manager.detect_settings_file(prefer_global=args.use_global)

    # Apply permissions
    success = manager.add_permissions(
        allow_rules=allow_rules,
        deny_rules=deny_rules,
        settings_path=settings_path,
        create_backup=not args.no_backup
    )

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
