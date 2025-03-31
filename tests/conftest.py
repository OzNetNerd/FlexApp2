"""
Pytest fixtures for app testing.
"""

import pytest
import sys
import os

# Add the parent directory to sys.path to find the app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import User
from app.models.base import db as _db
from app.routes.web.auth import auth_bp
from app.routes.web.main import main_bp
from .fixtures.mock_data import TEST_USERS


@pytest.fixture(scope='session')
def app():
    """Create and configure a Flask app for testing."""
    from flask import Flask
    from flask_login import LoginManager

    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY='test_secret_key',
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,  # Disable CSRF for testing
        SERVER_NAME='127.0.0.1:5000'
    )

    # Initialize extensions
    _db.init_app(app)

    # Setup login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    # Create context
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Create a database for the tests."""
    with app.app_context():
        _db.create_all()

        # Add test users
        for user_data in TEST_USERS:
            user = User(
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                name=user_data['name'],
                is_active=user_data['is_active']
            )
            _db.session.add(user)

        _db.session.commit()

        yield _db

        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session['_user_id'] = '1'  # User ID of test@example.com
        session['_fresh'] = True

    yield client


@pytest.fixture
def mock_user():
    """Return a mock user for testing."""
    return TEST_USERS[0]