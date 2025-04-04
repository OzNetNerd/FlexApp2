"""
Execute this script to create a pytest.ini file that skips database-dependent tests.
This makes it easier to focus on basic tests that don't need database access.
"""

import os

PYTEST_INI_CONTENT = """
[pytest]
markers =
    db: marks tests that require database access
python_files = test_*.py
python_classes = Test*
python_functions = test_*
testpaths = tests
norecursedirs = .git venv env build dist
addopts = -v -k "not db"
"""


def create_pytest_ini():
    """Create a pytest.ini file in the current directory."""
    with open("pytest.ini", "w") as f:
        f.write(PYTEST_INI_CONTENT)
    print("Created pytest.ini with settings to skip database tests.")
    print("Run 'pytest' to run only non-database tests.")
    print("Run 'pytest -k \"\"' to run all tests including database tests.")


if __name__ == "__main__":
    create_pytest_ini()
