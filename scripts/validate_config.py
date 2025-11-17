#!/usr/bin/env python3
"""
Configuration Validator for Claude Code Permissions

Validates permission rules for syntax errors, conflicts, and security issues.

Usage:
    validate_config.py <settings-file>
    validate_config.py --check-conflicts ~/.claude/settings.json
"""

import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Set


class PermissionValidator:
    """Validates Claude Code permission configurations."""

    VALID_TOOLS = {
        'Bash', 'Read', 'Write', 'Edit', 'WebFetch', 'WebSearch',
        'SlashCommand', 'NotebookEdit'
    }

    SENSITIVE_PATTERNS = [
        '.env', '*.key', '*.pem', '.aws', '.ssh', 'secrets',
        'credentials', 'password', 'token', 'private'
    ]

    DANGEROUS_COMMANDS = [
        'rm ', 'sudo ', 'chmod ', 'chown ', 'dd ', 'mkfs ',
        '| bash', '| sh', '--force', 'DELETE', 'DROP'
    ]

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    def validate_rule_syntax(self, rule: str) -> bool:
        """
        Validate syntax of a single permission rule.

        Args:
            rule: Permission rule string

        Returns:
            True if valid, False otherwise
        """
        # Empty rule
        if not rule or not rule.strip():
            self.errors.append(f"Empty permission rule")
            return False

        rule = rule.strip()

        # Check if it's just a tool name
        if rule in self.VALID_TOOLS:
            return True

        # Check if it's Tool(pattern) format
        if '(' not in rule:
            self.errors.append(f"Invalid format: '{rule}'. Expected 'ToolName' or 'ToolName(pattern)'")
            return False

        try:
            tool, pattern_part = rule.split('(', 1)

            # Validate tool name
            if tool not in self.VALID_TOOLS:
                self.errors.append(
                    f"Unknown tool: '{tool}' in rule '{rule}'. "
                    f"Valid tools: {', '.join(sorted(self.VALID_TOOLS))}"
                )
                return False

            # Check closing parenthesis
            if not pattern_part.endswith(')'):
                self.errors.append(f"Missing closing parenthesis in: '{rule}'")
                return False

            # Extract pattern
            pattern = pattern_part[:-1]

            # Validate pattern is not empty
            if not pattern:
                self.warnings.append(f"Empty pattern in rule: '{rule}' - this allows all operations for {tool}")

            return True

        except Exception as e:
            self.errors.append(f"Parse error in '{rule}': {e}")
            return False

    def check_security_issues(self, rule: str, is_deny: bool = False):
        """
        Check for potential security issues in a permission rule.

        Args:
            rule: Permission rule string
            is_deny: Whether this is a deny rule
        """
        rule_lower = rule.lower()

        # Check for sensitive file patterns in allow rules
        if not is_deny:
            for pattern in self.SENSITIVE_PATTERNS:
                if pattern in rule_lower:
                    self.warnings.append(
                        f"Potentially sensitive pattern in allow rule: '{rule}' (contains '{pattern}')"
                    )

        # Check for dangerous commands
        if 'Bash(' in rule or 'bash(' in rule_lower:
            for cmd in self.DANGEROUS_COMMANDS:
                if cmd.lower() in rule_lower:
                    if is_deny:
                        self.info.append(f"✓ Good practice: Denying dangerous operation: '{rule}'")
                    else:
                        self.warnings.append(
                            f"⚠️  Dangerous command pattern in allow rule: '{rule}' (contains '{cmd}')"
                        )

    def check_conflicts(self, allow_rules: List[str], deny_rules: List[str]) -> List[str]:
        """
        Check for conflicts between allow and deny rules.

        Args:
            allow_rules: List of allow rules
            deny_rules: List of deny rules

        Returns:
            List of conflict descriptions
        """
        conflicts = []

        # Convert rules to comparable format
        def normalize_rule(rule: str) -> Tuple[str, str]:
            """Return (tool, pattern) tuple."""
            if '(' not in rule:
                return (rule, '')
            tool, pattern = rule.split('(', 1)
            return (tool, pattern.rstrip(')'))

        # Check each allow rule against deny rules
        for allow in allow_rules:
            allow_tool, allow_pattern = normalize_rule(allow)

            for deny in deny_rules:
                deny_tool, deny_pattern = normalize_rule(deny)

                # Same tool
                if allow_tool == deny_tool:
                    # Exact match
                    if allow_pattern == deny_pattern:
                        conflicts.append(
                            f"Exact conflict: '{allow}' is both allowed and denied"
                        )
                    # Empty pattern conflicts (allow/deny all)
                    elif not allow_pattern or not deny_pattern:
                        conflicts.append(
                            f"Broad conflict: '{allow}' vs '{deny}'"
                        )
                    # Pattern overlap (basic check)
                    elif allow_pattern and deny_pattern:
                        # Check for obvious overlaps
                        if allow_pattern in deny_pattern or deny_pattern in allow_pattern:
                            self.warnings.append(
                                f"Potential overlap: '{allow}' and '{deny}' may conflict"
                            )

        return conflicts

    def check_deny_coverage(self, deny_rules: List[str]):
        """
        Check if important security deny rules are present.

        Args:
            deny_rules: List of deny rules
        """
        recommended_denies = {
            'Read(.env*)': 'Environment files',
            'Read(*.key)': 'Private key files',
            'Read(*.pem)': 'Certificate files',
            'Bash(rm *)': 'Dangerous rm command',
            'Bash(sudo *)': 'Sudo privilege escalation',
        }

        deny_str = ' '.join(deny_rules)

        for pattern, description in recommended_denies.items():
            # Simple substring check
            found = False
            for deny in deny_rules:
                if pattern.split('(')[1].rstrip(')') in deny:
                    found = True
                    break

            if not found:
                self.info.append(
                    f"💡 Consider adding deny rule for {description}: {pattern}"
                )

    def validate_settings_file(self, file_path: Path) -> bool:
        """
        Validate entire settings file.

        Args:
            file_path: Path to settings file

        Returns:
            True if valid, False if errors found
        """
        # Check file exists
        if not file_path.exists():
            self.errors.append(f"File not found: {file_path}")
            return False

        # Read JSON
        try:
            with open(file_path, 'r') as f:
                settings = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False

        # Check permissions structure
        if 'permissions' not in settings:
            self.warnings.append("No 'permissions' key found in settings")
            return True  # Not an error, just no permissions configured

        permissions = settings['permissions']

        # Validate allowedTools
        allow_rules = permissions.get('allowedTools', [])
        if allow_rules:
            self.info.append(f"Found {len(allow_rules)} allow rule(s)")

            for rule in allow_rules:
                if self.validate_rule_syntax(rule):
                    self.check_security_issues(rule, is_deny=False)

        # Validate deny rules
        deny_rules = permissions.get('deny', [])
        if deny_rules:
            self.info.append(f"Found {len(deny_rules)} deny rule(s)")

            for rule in deny_rules:
                if self.validate_rule_syntax(rule):
                    self.check_security_issues(rule, is_deny=True)

        # Check for conflicts
        if allow_rules and deny_rules:
            conflicts = self.check_conflicts(allow_rules, deny_rules)
            if conflicts:
                for conflict in conflicts:
                    self.errors.append(f"Conflict: {conflict}")

        # Check deny coverage
        if allow_rules:  # Only suggest denies if there are allows
            self.check_deny_coverage(deny_rules)

        return len(self.errors) == 0

    def print_results(self, verbose: bool = False):
        """
        Print validation results.

        Args:
            verbose: Whether to print info messages
        """
        if self.errors:
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"   {error}")
            print()

        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")
            print()

        if verbose and self.info:
            print("ℹ️  INFO:")
            for info in self.info:
                print(f"   {info}")
            print()

        # Summary
        if not self.errors and not self.warnings:
            print("✅ Validation passed - no errors or warnings")
        elif not self.errors:
            print(f"✅ Validation passed - {len(self.warnings)} warning(s)")
        else:
            print(f"❌ Validation failed - {len(self.errors)} error(s), {len(self.warnings)} warning(s)")


def main():
    parser = argparse.ArgumentParser(
        description='Validate Claude Code permission configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'file',
        type=Path,
        help='Path to settings.json file to validate'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show informational messages'
    )

    parser.add_argument(
        '--check-conflicts',
        action='store_true',
        help='Only check for conflicts between allow and deny rules'
    )

    args = parser.parse_args()

    validator = PermissionValidator()

    # Validate the file
    is_valid = validator.validate_settings_file(args.file)

    # Print results
    validator.print_results(verbose=args.verbose)

    # Exit code
    return 0 if is_valid else 1


if __name__ == '__main__':
    sys.exit(main())
