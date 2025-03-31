# Testing the Login Functionality

This directory contains tests for the login functionality of the CRM application. The tests are organized to allow for incremental development and verification.

## Running Tests

### Run Basic Tests Only (No Database Required)

```bash
# Run all tests that don't require database interaction
pytest -k "not db"

# Run just the basic auth tests
pytest tests/unit/test_auth_basic.py tests/unit/test_auth_routes.py -v
```

### Run Specific Test Files

```bash
# Run a specific test file
pytest tests/unit/test_auth_routes.py -v

# Run the login redirect test
pytest tests/unit/test_login_redirect.py -v

# Run all login tests
pytest -k "login" -v
```

### Run All Tests

```bash
# Run all tests
pytest
```

## Test Organization

### Unit Tests

- `test_auth_routes.py` - Basic tests for auth routes
- `test_auth_basic.py` - Additional basic authentication tests
- `test_auth_additional.py` - Tests for auth endpoints
- `test_login_view.py` - Tests for login view
- `test_login_redirect.py` - Tests for login redirection
- `test_basic.py` - Simple sanity check test

### Model Tests

- `test_user_model.py` - Tests for the User model

### Functional Tests

- `test_auth_flow.py` - Tests for the authentication flow
- `test_mock_auth.py` - Mock-based tests for authentication

## Helper Scripts

- `skip_db_tests.py` - Creates a pytest.ini file to skip database tests
- `mark_db_tests.py` - Adds database markers to test functions

## Next Steps for Testing

1. Start by running the basic tests that don't require database interaction
2. Fix any issues with route configurations or template paths
3. Run the model tests to verify your User model works correctly
4. Finally, run the full authentication flow tests

## Common Issues and Solutions

### Database Tests Failing

- Use `python skip_db_tests.py` to create a pytest.ini that skips database tests
- Or run `pytest -k "not db"` to skip database tests

### Route Not Found (404) Issues

- Check that your Flask app is registering blueprints correctly
- Verify URL prefixes in your test client

### Template Not Found Issues

- Make sure your Flask app's template_folder is set correctly
- Check that test templates are in the correct location

### Authentication Flow Issues

- Verify your login_manager configuration
- Check that your User model implements the Flask-Login UserMixin interface