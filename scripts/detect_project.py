#!/usr/bin/env python3
"""
Project Type Detection for Claude Code Permissions

Auto-detects project type based on indicator files and recommends
appropriate permission templates.

Usage:
    detect_project.py [directory]
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import Counter


class ProjectDetector:
    """Detects project type by scanning for language/framework indicators."""

    # Indicator files for each project type
    INDICATORS = {
        'rust': ['Cargo.toml', 'Cargo.lock'],
        'java-maven': ['pom.xml'],
        'java-gradle': ['build.gradle', 'build.gradle.kts', 'settings.gradle', 'settings.gradle.kts'],
        'typescript': ['tsconfig.json'],
        'javascript': ['package.json'],
        'python': ['pyproject.toml', 'setup.py', 'requirements.txt', 'Pipfile'],
        'go': ['go.mod', 'go.sum'],
        'ruby': ['Gemfile', 'Gemfile.lock', '.ruby-version'],
        'php': ['composer.json', 'composer.lock'],
        'csharp': ['*.csproj', '*.sln'],
        'cpp': ['CMakeLists.txt', 'Makefile'],
        'swift': ['Package.swift', '*.xcodeproj'],
        'kotlin': ['build.gradle.kts'],
    }

    # File extensions for each language (for secondary detection)
    EXTENSIONS = {
        'rust': ['.rs'],
        'java': ['.java'],
        'typescript': ['.ts', '.tsx'],
        'javascript': ['.js', '.jsx'],
        'python': ['.py'],
        'go': ['.go'],
        'ruby': ['.rb'],
        'php': ['.php'],
        'csharp': ['.cs'],
        'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.h'],
        'swift': ['.swift'],
        'kotlin': ['.kt', '.kts'],
    }

    def __init__(self, directory: Path = None):
        """
        Initialize project detector.

        Args:
            directory: Directory to scan (defaults to current directory)
        """
        self.directory = directory or Path.cwd()

    def detect_by_indicators(self) -> Dict[str, List[str]]:
        """
        Detect project types by scanning for indicator files.

        Returns:
            Dictionary mapping project type to found indicators
        """
        found = {}

        for project_type, indicators in self.INDICATORS.items():
            matches = []

            for indicator in indicators:
                # Handle glob patterns (e.g., *.csproj)
                if '*' in indicator:
                    pattern_matches = list(self.directory.glob(indicator))
                    if pattern_matches:
                        matches.extend([p.name for p in pattern_matches])
                else:
                    # Exact file match
                    if (self.directory / indicator).exists():
                        matches.append(indicator)

            if matches:
                found[project_type] = matches

        return found

    def count_file_extensions(self, max_depth: int = 3) -> Counter:
        """
        Count source file extensions in directory.

        Args:
            max_depth: Maximum directory depth to scan

        Returns:
            Counter of file extensions
        """
        extensions = Counter()

        def scan_dir(dir_path: Path, depth: int):
            if depth > max_depth:
                return

            try:
                for item in dir_path.iterdir():
                    # Skip hidden directories and common build/dependency dirs
                    if item.is_dir():
                        name = item.name
                        if name.startswith('.') or name in ['node_modules', 'target', 'build', 'dist', '__pycache__', 'venv']:
                            continue
                        scan_dir(item, depth + 1)
                    elif item.is_file():
                        ext = item.suffix
                        if ext:
                            extensions[ext] += 1
            except PermissionError:
                pass  # Skip directories we can't read

        scan_dir(self.directory, 0)
        return extensions

    def detect_by_extensions(self) -> List[str]:
        """
        Detect likely languages by counting file extensions.

        Returns:
            List of detected project types sorted by file count
        """
        extension_counts = self.count_file_extensions()

        # Map extensions to project types with counts
        type_counts = Counter()

        for ext, count in extension_counts.items():
            for project_type, exts in self.EXTENSIONS.items():
                if ext in exts:
                    type_counts[project_type] += count

        # Return types sorted by count (most files first)
        return [ptype for ptype, _ in type_counts.most_common()]

    def detect_all(self) -> Tuple[List[str], Dict[str, any]]:
        """
        Detect all project types using both indicators and extensions.

        Returns:
            Tuple of (detected_types, metadata)
            - detected_types: List of project types (primary first)
            - metadata: Dict with detection details
        """
        # Detect by indicators (most reliable)
        indicator_matches = self.detect_by_indicators()

        # Detect by file extensions (secondary check)
        extension_types = self.detect_by_extensions()

        # Combine results - prioritize indicator-based detection
        detected = []
        seen = set()

        # Add indicator-based detections first
        for ptype in indicator_matches.keys():
            if ptype not in seen:
                detected.append(ptype)
                seen.add(ptype)

        # Add extension-based detections for languages not yet detected
        for ptype in extension_types:
            # Map language back to project type if needed
            base_lang = ptype
            if base_lang not in seen:
                # Check if we have a more specific variant detected
                if base_lang == 'java' and 'java-maven' not in seen and 'java-gradle' not in seen:
                    detected.append('java-maven')  # Default to Maven if no build tool detected
                    seen.add(base_lang)
                elif base_lang in ['java', 'typescript', 'javascript']:
                    # These have specific variants, skip if variant already detected
                    pass
                else:
                    detected.append(base_lang)
                    seen.add(base_lang)

        # Handle special cases
        # TypeScript projects always have JavaScript too
        if 'typescript' in detected and 'javascript' not in detected:
            # Check if package.json exists
            if (self.directory / 'package.json').exists():
                detected.insert(detected.index('typescript') + 1, 'javascript')

        metadata = {
            'indicators': indicator_matches,
            'extension_detection': extension_types[:5],  # Top 5
            'primary': detected[0] if detected else None,
            'secondary': detected[1:] if len(detected) > 1 else []
        }

        return (detected, metadata)

    def recommend_template(self, project_types: List[str]) -> Optional[str]:
        """
        Recommend permission template based on detected types.

        Args:
            project_types: List of detected project types

        Returns:
            Recommended template name or None
        """
        if not project_types:
            return None

        # Return primary type
        return project_types[0]

    def load_templates(self) -> Dict:
        """
        Load project templates from references directory.

        Returns:
            Dictionary of templates
        """
        templates_path = Path(__file__).parent.parent / 'references' / 'project_templates.json'

        if not templates_path.exists():
            return {}

        with open(templates_path, 'r') as f:
            return json.load(f)

    def get_permissions_for_types(self, project_types: List[str]) -> Tuple[List[str], List[str]]:
        """
        Get permission rules for detected project types.

        Args:
            project_types: List of detected project types

        Returns:
            Tuple of (allow_rules, deny_rules)
        """
        templates = self.load_templates()

        allow_rules = []
        deny_rules = []

        for ptype in project_types:
            if ptype in templates:
                template = templates[ptype]

                # Add file patterns
                if 'file_patterns' in template:
                    allow_rules.extend(template['file_patterns'].get('allow', []))
                    deny_rules.extend(template['file_patterns'].get('deny', []))

                # Add CLI commands
                if 'commands' in template:
                    allow_rules.extend(template['commands'].get('allow', []))
                    deny_rules.extend(template['commands'].get('deny', []))

        # Remove duplicates while preserving order
        allow_rules = list(dict.fromkeys(allow_rules))
        deny_rules = list(dict.fromkeys(deny_rules))

        return (allow_rules, deny_rules)


def main():
    """CLI interface for project detection."""
    import argparse

    parser = argparse.ArgumentParser(description='Detect project type and recommend permissions')
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to scan (default: current directory)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    parser.add_argument(
        '--permissions',
        action='store_true',
        help='Output recommended permission rules'
    )

    args = parser.parse_args()

    directory = Path(args.directory).resolve()

    if not directory.exists():
        print(f"❌ Directory not found: {directory}", file=sys.stderr)
        return 1

    if not directory.is_dir():
        print(f"❌ Not a directory: {directory}", file=sys.stderr)
        return 1

    detector = ProjectDetector(directory)
    detected_types, metadata = detector.detect_all()

    if args.json:
        output = {
            'directory': str(directory),
            'detected_types': detected_types,
            'metadata': metadata
        }

        if args.permissions:
            allow, deny = detector.get_permissions_for_types(detected_types)
            output['permissions'] = {
                'allowedTools': allow,
                'deny': deny
            }

        print(json.dumps(output, indent=2))
        return 0

    # Human-readable output
    print(f"📁 Scanning: {directory}")
    print()

    if not detected_types:
        print("❌ No project type detected")
        print("   This might be an empty directory or an unsupported project type.")
        return 1

    print("✅ Detected project type(s):")
    print()

    # Primary type
    primary = detected_types[0]
    print(f"   Primary: {primary.upper()}")

    if metadata['indicators'].get(primary):
        print(f"   Indicators: {', '.join(metadata['indicators'][primary])}")

    # Secondary types
    if len(detected_types) > 1:
        print()
        print("   Secondary:")
        for stype in detected_types[1:]:
            print(f"   - {stype}")
            if metadata['indicators'].get(stype):
                print(f"     Indicators: {', '.join(metadata['indicators'][stype])}")

    if args.permissions:
        print()
        print("📋 Recommended permissions:")
        print()

        allow, deny = detector.get_permissions_for_types(detected_types)

        if allow:
            print("   Allow:")
            for rule in allow:
                print(f"   - {rule}")

        if deny:
            print()
            print("   Deny:")
            for rule in deny:
                print(f"   - {rule}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
