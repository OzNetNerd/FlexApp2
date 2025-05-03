"""
Add database test markers to test files.

This script scans all test files and adds @pytest.mark.db markers to tests
that use the db fixture, making it easier to selectively run or skip them.
"""

import re
from pathlib import Path


def add_db_markers(filepath):
    """Add @pytest.mark.db to tests that use the db fixture."""
    with open(filepath, "r") as f:
        content = f.read()

    # Check if pytest is already imported
    if "import pytest" not in content:
        content = "import pytest\n" + content

    # Find all test functions
    pattern = r"def\s+(test_[a-zA-Z0-9_]+)\s*\(([^)]*)\)"

    # For each test function that has 'db' in its parameters, add the marker
    def replace_with_marker(match):
        func_name = match.group(1)
        params = match.group(2)

        # If 'db' is in parameters, add the marker
        if "db" in params.split(","):
            return f"@pytest.mark.db\ndef {func_name}({params})"
        return match.group(0)

    modified_content = re.sub(pattern, replace_with_marker, content)

    # Write back the modified content if changes were made
    if modified_content != content:
        with open(filepath, "w") as f:
            f.write(modified_content)
        return True
    return False


def process_test_files():
    """Process all test files in the tests directory."""
    test_dir = Path("tests")
    count = 0

    for path in test_dir.glob("**/*.py"):
        if path.name.startswith("test_"):
            if add_db_markers(path):
                count += 1
                print(f"Added markers to {path}")

    print(f"Added DB markers to {count} files.")
    print("Now you can run 'pytest -k \"not db\"' to skip database tests.")


if __name__ == "__main__":
    process_test_files()