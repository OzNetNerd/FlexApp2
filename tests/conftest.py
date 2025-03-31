import pytest
import sys
import os

# Add the project root directory to sys.path so that app.py can be imported correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import User
from app.models.base import db as _db
from .fixtures.mock_data import TEST_USERS


@pytest.fixture(scope='session')
def app():
    """Create and configure the production Flask app for testing.

    This fixture sets up the Flask app for testing by configuring it with test-specific settings,
    such as an in-memory SQLite database, disabling CSRF, and other necessary configurations. It
    also creates all the necessary database tables for the tests and cleans them up after the tests.

    Asserts:
        - The app is correctly configured for testing.
    """
    # Import create_app from app.py (not from the app package)
    from app.app import create_app
    app = create_app()

    # Override configuration for testing purposes
    app.config.update(
        TESTING=True,
        SECRET_KEY='test_secret_key',
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
        SERVER_NAME='127.0.0.1:5000',
        SESSION_COOKIE_SECURE=False,  # Allow cookies over HTTP for testing
    )

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Create a new database for each test function.

    This fixture sets up a fresh database for each test by creating the necessary tables and
    adding mock user data. After the test, the database is cleaned up by removing all entries.

    Args:
        app (Flask): The Flask application fixture for running the app.

    Asserts:
        - The database contains mock users before the test function runs.
        - The database is cleaned up after the test function completes.
    """
    with app.app_context():
        _db.create_all()
        # Add test users from our mock data
        for user_data in TEST_USERS:
            user = User(
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                name=user_data['name']
            )
            # Explicitly set the user ID for testing purposes
            user.id = user_data['id']
            _db.session.add(user)
        _db.session.commit()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Return a test client for the app.

    This fixture provides a test client that can be used to simulate requests to the Flask app
    during testing.

    Args:
        app (Flask): The Flask application fixture for running the app.

    Asserts:
        - The test client is correctly set up and can make requests to the app.
    """
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Return an authenticated test client.

    This fixture simulates an authenticated user by modifying the session of the test client
    to include a user ID, allowing tests to simulate actions as an authenticated user.

    Args:
        client (FlaskClient): The test client fixture.

    Asserts:
        - The test client is authenticated for the duration of the test.
    """
    with client.session_transaction() as session:
        # Assuming TEST_USERS[0] has id '1'
        session['_user_id'] = '1'
        session['_fresh'] = True
    yield client


@pytest.fixture
def mock_user():
    """Return a mock user from the test data.

    This fixture provides mock user data that can be used in tests that require a user.

    Asserts:
        - The returned user data matches one of the entries in the mock data.
    """
    return TEST_USERS[0]
