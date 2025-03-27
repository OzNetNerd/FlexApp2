import os
import pytest
from flask import Flask
from app.app import create_app
from app.models.base import db
from app.models.user import User
from werkzeug.security import generate_password_hash


@pytest.fixture
def app() -> Flask:
    """
    Create a Flask test app with an in-memory SQLite database.

    Returns:
        Flask: The configured Flask application.
    """
    os.environ["FLASK_ENV"] = "testing"
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask):
    """
    Provides a Flask test client to simulate HTTP requests.

    Args:
        app (Flask): The test app fixture.

    Returns:
        FlaskClient: The test client for sending requests to the app.
    """
    return app.test_client()


@pytest.fixture
def test_user(app: Flask):
    """
    Creates a test user in the temporary test database.

    Args:
        app (Flask): The Flask application.

    Returns:
        User: The created test user object.
    """
    user = User(
        name="Test User",
        email="test@example.com",
        password=generate_password_hash("testpass"),  # Adjust depending on your User model
    )
    db.session.add(user)
    db.session.commit()
    return user
