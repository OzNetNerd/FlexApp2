"""Test Structure Synchronizer.

This module ensures pytest files and directories match the application structure.
It creates test files and directories that mirror the app structure and identifies
stale test files that no longer have corresponding app files.
"""

import os
import sys
import argparse
import fnmatch
import shutil
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional, Any

DEFAULT_EXEMPT_PREFIXES = ["fixtures", "functional", "integrations", "unit"]


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed command line arguments.
    """
    # Default exempt prefixes

    parser = argparse.ArgumentParser(description="Sync test structure with app structure")
    parser.add_argument("--app-dir", default="app", help="Application directory (default: app)")
    parser.add_argument("--test-dir", default="tests", help="Test directory (default: tests)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--ignore-file", default=".testignore", help="File containing ignore patterns (default: .testignore)")
    parser.add_argument("--clean", action="store_true", help="Remove stale test files/directories")
    parser.add_argument(
        "--template", choices=["basic", "pytest", "unittest"], default="pytest", help="Test file template (default: pytest)"
    )
    parser.add_argument("--exempt-prefixes", nargs="+", default=[], help="Additional test directory prefixes to exempt from stale checking")

    args = parser.parse_args()

    # Combine default exempt prefixes with user-provided ones
    args.exempt_prefixes = DEFAULT_EXEMPT_PREFIXES + args.exempt_prefixes

    return args


def get_ignore_patterns(ignore_file: str) -> List[str]:
    """Load ignore patterns from file if it exists.

    Args:
        ignore_file (str): Path to the file containing ignore patterns.

    Returns:
        List[str]: List of ignore patterns.
    """
    patterns = []
    if os.path.exists(ignore_file):
        with open(ignore_file, "r") as f:
            patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return patterns


def is_ignored(path: str, ignore_patterns: List[str]) -> bool:
    """Check if a path matches any ignore pattern.

    Args:
        path (str): The path to check.
        ignore_patterns (List[str]): List of patterns to check against.

    Returns:
        bool: True if the path matches any pattern, False otherwise.
    """
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False


def get_relative_paths(base_dir: str, ignore_patterns: List[str]) -> Set[str]:
    """Walk a directory tree and return a set of relative file paths.

    Args:
        base_dir (str): The base directory to walk.
        ignore_patterns (List[str]): Patterns to ignore.

    Returns:
        Set[str]: Set of relative file paths.
    """
    paths = set()
    for root, dirs, files in os.walk(base_dir):
        # Filter directories using ignore patterns
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), ignore_patterns)]

        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                full_path = os.path.join(root, file)
                if not is_ignored(full_path, ignore_patterns):
                    rel_path = os.path.relpath(full_path, base_dir)
                    paths.add(rel_path)
    return paths


def create_test_stub(file_path: str, module_path: str, template_type: str) -> str:
    """Create a test file stub based on the template type.

    Args:
        file_path (str): The path to the file being tested.
        module_path (str): The module path for imports.
        template_type (str): The type of template to use.

    Returns:
        str: The content of the test stub.
    """
    app_module = module_path.replace("/", ".").replace(".py", "")

    if template_type == "basic":
        return f"""# Tests for {app_module}
# Created: {datetime.now().strftime('%Y-%m-%d')}

def test_module_imports():
    '''Test that the module can be imported.'''
    try:
        from {app_module} import *
        assert True
    except ImportError:
        assert False, f"Failed to import {app_module}"
"""
    elif template_type == "pytest":
        return f"""# Tests for {app_module}
# Created: {datetime.now().strftime('%Y-%m-%d')}
import pytest
from {app_module} import *

def test_module_imports():
    '''Test that the module can be imported.'''
    assert True, "Module imported successfully"

# TODO: Add more specific tests
"""
    elif template_type == "unittest":
        return f"""# Tests for {app_module}
# Created: {datetime.now().strftime('%Y-%m-%d')}
import unittest
from {app_module} import *

class Test{os.path.basename(file_path).replace('.py', '').title()}(unittest.TestCase):
    def setUp(self):
        '''Set up test fixtures.'''
        pass

    def tearDown(self):
        '''Tear down test fixtures.'''
        pass

    def test_module_imports(self):
        '''Test that the module can be imported.'''
        self.assertTrue(True, "Module imported successfully")

if __name__ == '__main__':
    unittest.main()
"""


def ensure_test_structure(app_file_paths: Set[str], args: argparse.Namespace) -> Tuple[int, int, int]:
    """Ensure test structure and files match app structure.

    Args:
        app_file_paths (Set[str]): Set of relative paths to app files.
        args (argparse.Namespace): Command-line arguments.

    Returns:
        Tuple[int, int, int]: Count of created directories, test files, and init files.
    """
    created_dirs_count = 0
    created_files_count = 0
    created_inits_count = 0

    for rel_path in app_file_paths:
        # Build mirrored test directory and file path
        test_rel_dir = os.path.dirname(rel_path)
        test_dir_path = os.path.join(args.test_dir, test_rel_dir)
        test_filename = f"test_{os.path.basename(rel_path)}"
        test_file_path = os.path.join(test_dir_path, test_filename)

        # Create test directory if missing
        if not os.path.exists(test_dir_path):
            if not args.dry_run:
                try:
                    os.makedirs(test_dir_path, exist_ok=True)
                    print(f"[DIR CREATED] {test_dir_path}")
                    created_dirs_count += 1
                except OSError as e:
                    print(f"ERROR: Failed to create directory {test_dir_path}: {e}", file=sys.stderr)
            else:
                print(f"[WOULD CREATE DIR] {test_dir_path}")
                created_dirs_count += 1

        # Create __init__.py in each directory level
        if not args.dry_run:
            # Create __init__.py files in all parent directories
            parts = test_rel_dir.split(os.sep)
            current_path = args.test_dir
            for part in parts:
                if part:  # Skip empty parts
                    current_path = os.path.join(current_path, part)
                    init_file = os.path.join(current_path, "__init__.py")
                    if not os.path.exists(init_file):
                        try:
                            with open(init_file, "w") as f:
                                f.write(f"# Test package for {current_path}\n")
                            print(f"[INIT CREATED] {init_file}")
                            created_inits_count += 1
                        except OSError as e:
                            print(f"ERROR: Failed to create {init_file}: {e}", file=sys.stderr)

        # Create test file if missing
        if not os.path.exists(test_file_path):
            if not args.dry_run:
                try:
                    app_module = f"{args.app_dir}.{rel_path.replace(os.sep, '.').replace('.py', '')}"
                    test_content = create_test_stub(rel_path, app_module, args.template)
                    with open(test_file_path, "w") as tf:
                        tf.write(test_content)
                    print(f"[FILE CREATED] {test_file_path}")
                    created_files_count += 1
                except OSError as e:
                    print(f"ERROR: Failed to create {test_file_path}: {e}", file=sys.stderr)
            else:
                print(f"[WOULD CREATE FILE] {test_file_path}")
                created_files_count += 1

    # Create or ensure root __init__.py
    root_init = os.path.join(args.test_dir, "__init__.py")
    if not os.path.exists(root_init) and not args.dry_run:
        try:
            with open(root_init, "w") as f:
                f.write(f"# Root test package\n")
            print(f"[INIT CREATED] {root_init}")
            created_inits_count += 1
        except OSError as e:
            print(f"ERROR: Failed to create {root_init}: {e}", file=sys.stderr)

    return created_dirs_count, created_files_count, created_inits_count


def find_stale_test_dirs(app_file_paths: Set[str], args: argparse.Namespace) -> List[str]:
    """Find test directories that no longer have a corresponding app directory.

    Identifies test directories that don't have matching app directories,
    excluding directories that match exempt prefixes.

    Args:
        app_file_paths: Set of relative paths to app files.
        args: Command-line arguments including exempt_prefixes.

    Returns:
        List of stale test directory paths.
    """
    # Get valid directory paths based on app structure
    valid_test_dirs = {os.path.dirname(p) for p in app_file_paths}
    valid_test_dirs.add("")  # Add root directory

    # Find all test directories
    found_test_dirs = set()
    for root, dirs, _ in os.walk(args.test_dir):
        for dir_name in dirs:
            if dir_name != "__pycache__":  # Skip __pycache__ directories
                test_subdir = os.path.relpath(os.path.join(root, dir_name), args.test_dir)
                found_test_dirs.add(test_subdir)

    # Get potentially stale directories (not in app structure)
    potentially_stale = found_test_dirs - valid_test_dirs

    # Filter out exempted prefixes
    stale_dirs_list = []
    for dir_path in sorted(potentially_stale):
        # Skip if directory matches any exempted prefix
        if any(dir_path == prefix or dir_path.startswith(f"{prefix}/") for prefix in args.exempt_prefixes):
            continue

        stale_dir_path = os.path.join(args.test_dir, dir_path)
        stale_dirs_list.append(stale_dir_path)
        print(f"[STALE DIR] {stale_dir_path}")

        if args.clean and not args.dry_run:
            try:
                shutil.rmtree(stale_dir_path)
                print(f"[REMOVED DIR] {stale_dir_path}")
            except OSError as e:
                print(f"ERROR: Failed to remove {stale_dir_path}: {e}", file=sys.stderr)
        elif args.clean and args.dry_run:
            print(f"[WOULD REMOVE DIR] {stale_dir_path}")

    return stale_dirs_list


def find_stale_test_files(app_file_paths: Set[str], args: argparse.Namespace) -> List[str]:
    """Find test files that no longer have a corresponding app file.

    Args:
        app_file_paths: Set of relative paths to app files.
        args: Command-line arguments including exempt_prefixes.

    Returns:
        List of stale test file paths.
    """
    # Create mapping of expected test files
    expected_test_files = {}
    for path in app_file_paths:
        dir_name = os.path.dirname(path)
        file_name = f"test_{os.path.basename(path)}"
        test_path = os.path.join(dir_name, file_name)
        expected_test_files[test_path] = True

    stale_files = []

    for root, _, files in os.walk(args.test_dir):
        for file_name in files:
            if file_name.startswith("test_") and file_name.endswith(".py"):
                rel_path = os.path.relpath(os.path.join(root, file_name), args.test_dir)

                # Skip if file is in an exempted directory
                rel_dir = os.path.dirname(rel_path)
                if any(rel_dir == prefix or rel_dir.startswith(f"{prefix}/") for prefix in args.exempt_prefixes):
                    continue

                if rel_path not in expected_test_files:
                    stale_file_path = os.path.join(args.test_dir, rel_path)
                    stale_files.append(stale_file_path)
                    print(f"[STALE FILE] {stale_file_path}")

                    if args.clean and not args.dry_run:
                        try:
                            os.remove(stale_file_path)
                            print(f"[REMOVED FILE] {stale_file_path}")
                        except OSError as e:
                            print(f"ERROR: Failed to remove {stale_file_path}: {e}", file=sys.stderr)
                    elif args.clean and args.dry_run:
                        print(f"[WOULD REMOVE FILE] {stale_file_path}")

    return stale_files


def main() -> int:
    """Main function to sync test structure with app structure.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    args = parse_arguments()

    # Check if directories exist
    if not os.path.isdir(args.app_dir):
        print(f"ERROR: App directory '{args.app_dir}' does not exist", file=sys.stderr)
        return 1

    if not args.dry_run and not os.path.exists(args.test_dir):
        try:
            os.makedirs(args.test_dir)
            print(f"[DIR CREATED] {args.test_dir}")
        except OSError as e:
            print(f"ERROR: Failed to create test directory '{args.test_dir}': {e}", file=sys.stderr)
            return 1

    # Load ignore patterns
    ignore_patterns = get_ignore_patterns(args.ignore_file)

    print(f"🔄 Syncing test structure with app structure...\n")
    print(f"App directory: {args.app_dir}")
    print(f"Test directory: {args.test_dir}")
    print(f"Template type: {args.template}")
    if args.dry_run:
        print("Running in DRY-RUN mode (no changes will be made)")
    if args.clean:
        print("Clean mode: Will remove stale test files/directories")
    if ignore_patterns:
        print(f"Using {len(ignore_patterns)} ignore patterns from {args.ignore_file}")
    print()

    # Get app file paths
    app_file_paths = get_relative_paths(args.app_dir, ignore_patterns)

    # Ensure test structure
    created_dirs, created_files, created_inits = ensure_test_structure(app_file_paths, args)

    # Find stale test dirs and files
    stale_dirs = find_stale_test_dirs(app_file_paths, args)
    stale_files = find_stale_test_files(app_file_paths, args)

    print("\n✅ Sync complete.")
    print(f"  📊 Stats:")
    print(f"    ➕ App files found: {len(app_file_paths)}")
    print(f"    ➕ Directories created: {created_dirs}")
    print(f"    📝 Test files created: {created_files}")
    print(f"    📝 __init__.py files created: {created_inits}")
    print(f"    ⚠️ Stale test dirs flagged: {len(stale_dirs)}")
    print(f"    ⚠️ Stale test files flagged: {len(stale_files)}")

    if args.dry_run:
        print("\n⚠️ This was a dry run. No actual changes were made.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
