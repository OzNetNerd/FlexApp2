# Claude

```
Write pytest tests for the following files. I have all the code I need to set up flask, etc, I just need the tests
```

# Codecov

```
clear && pytest --cov=. --cov-report=term-missing --cov-config=.coveragerc

```

# Pytest
## Setup

Activate venv:

```
clear && source /mnt/c/Will/code/FlexApp2/venv/bin/activate
```

Get tree:

```
clear &&  tree -P '*.py' -I 'venv' --prune
```

Run tests:

```
clear && pytest -v --markers
clear && pytest -v
clear && pytest -vvs tests/functional/test_mock_auth.py
clear && pytest tests/unit/utils/test_model_registry.py
clear && pytest --collect-only
clear && pytest -v --rootdir=/mnt/c/Will/code/FlexApp2 -c=/mnt/c/Will/code/FlexApp2/pytest.ini
```

```
# Doesn't work
# clear && pytest --config=pytest.ini
```

## Basic Test Execution

```
# Run all tests
pytest

# Run non-database tests only
pytest -k "not db"

# Run with coverage reporting
pytest --cov=app

# Run specific test file
pytest tests/path/to/test_file.py

# Run tests by marker
pytest -m "unit"  # run unit tests
pytest -m "integration"  # run integration tests
```

## Setup Scripts

MMark database tests:

```
python mark_db_tests.py
```

Configure pytest to skip DB tests:

```
python skip_db_tests.py
```

Temporarily disable DB tests (alternative method):

```
cp conftest_skip.py tests/conftest_skip.py
```

## Database Test Management

Mark database tests:

```
python mark_db_tests.py
```

This adds `@pytest.mark.db` to tests that use the **db fixture**.

Skip database tests automatically:

```
python skip_db_tests.py
```

This creates a `pytest.ini` file with `-k "not db"` configuration.


Use conftest_skip.py to temporarily disable db tests:

```
cp conftest_skip.py tests/conftest_skip.py
```

## Specific Test Groups

Run specific test files:

```
pytest tests/path/to/test_file.py
```

Run tests with verbose output:

```
pytest -v
```

================================

# Test Structure Recommendations
## Current Test Organization Assessment
Your existing structure follows good practices with separate directories for unit, functional, and integration tests. However, test coverage is low (34%) with several modules at 0%, and tests are heavily focused on auth functionality.
Recommendations for Test Structure

## 1. Mirror your application structure in the unit test directory:
```
unit/
  models/
  routes/
    api/
    web/
  services/
  utils/
```

## 2. Create test files that match source files (1:1 relationship):

For each module with low coverage, create a corresponding test file
Example: 

```
app/services/srs_service.py → unit/services/test_srs_service.py
```

## 3. Prioritize testing critical services:
* Focus first on services/srs_service.py (11% coverage)
* Then services/relationship_service.py and category_service.py (0% coverage)
* Follow with web components and routes

## 4. Add integration tests for API endpoints and web routes
## 5. Use fixtures effectively to reduce test setup duplication

## Should You Reorganize Existing Tests?
Yes, but minimally:

* Keep your current unit/functional/integration separation
* Move existing auth unit tests into unit/services/ or appropriate subdirectories
* Maintain your existing fixtures
* The focus should be on expanding coverage rather than extensive reorganization.