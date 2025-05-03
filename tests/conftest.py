"""
Pytest configuration file that defines fixtures for testing.

This file provides common fixtures that can be used across all tests, including database setup,
test client setup, and authenticated client setup. It also provides convenience fixtures for
accessing mock data.
"""
import os
import sys
import pytest

# Add the project root directory to sys.path so that imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.base import db as _db
from app.models.pages.user import User

from .fixtures.mock_data import TEST_USERS

# Global variable to track if we've registered the blueprints
_app_instance = None

@pytest.fixture(scope="session")
def app():
    """Create and configure the Flask app for testing."""
    global _app_instance
    if _app_instance is not None:
        return _app_instance

    from app.app import create_app
    _app_instance = create_app()

    # Override configuration for testing
    _app_instance.config.update(
        TESTING=True,
        SECRET_KEY="test_secret_key",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
        SERVER_NAME="127.0.0.1:5000",
        SESSION_COOKIE_SECURE=False,
    )

    # Create app context for the session
    ctx = _app_instance.app_context()
    ctx.push()

    # Set up database initially
    _db.create_all()

    yield _app_instance

    # Clean up at end of session
    ctx.pop()
    _app_instance = None


@pytest.fixture(scope="function")
def db(app):
    """Create a new database for each test function."""
    _db.create_all()
    # Add test users from our mock data
    for user_data in TEST_USERS:
        user = User(
            email=user_data["email"],
            password_hash=user_data["password_hash"],
            name=user_data["name"],
            username=user_data.get("username")
        )
        # Explicitly set the user ID for testing
        user.id = user_data["id"]
        _db.session.add(user)
    _db.session.commit()

    yield _db

    # Clean up after test
    _db.session.remove()
    _db.drop_all()


@pytest.fixture
def client(app):
    """Return a test client for the app."""
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def auth_client(client):
    """Return an authenticated test client."""
    with client.session_transaction() as session:
        session["_user_id"] = "1"
        session["_fresh"] = True
    yield client


@pytest.fixture
def mock_user():
    """Return a mock user from the test data."""
    return TEST_USERS[0]

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "db: marks tests that require database access")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "functional: marks functional tests")
    config.addinivalue_line("markers", "unit: marks unit tests")
    config.addinivalue_line("markers", "slow: marks tests that are slow")