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
    """Create and configure the production Flask app for testing."""
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
    """Create a new database for each test function."""
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
    """Return a test client for the app."""
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Return an authenticated test client."""
    with client.session_transaction() as session:
        # Assuming TEST_USERS[0] has id '1'
        session['_user_id'] = '1'
        session['_fresh'] = True
    yield client


@pytest.fixture
def mock_user():
    """Return a mock user from the test data."""
    return TEST_USERS[0]
