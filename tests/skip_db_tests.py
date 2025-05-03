"""
Create a pytest.ini file that skips database-dependent tests.

This script creates a pytest.ini configuration that automatically excludes tests
marked with 'db', making it easier to run only lightweight tests.
"""

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