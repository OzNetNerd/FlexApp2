# Codecov

```
pytest --cov=. --cov-report=term-missing --cov-config=.coveragerc --skip-empty

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