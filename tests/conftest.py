"""Test configuration fixtures and utilities.

This module provides pytest fixtures and utility functions for testing the FlexApp application,
including database setup, application creation, and authentication helpers.
"""

import os
import sqlite3
import pytest
from flask import Flask
from app.app import create_app
from app.models.base import db
from app.models.user import User
from werkzeug.security import generate_password_hash


def copy_db_to_memory(source_path: str = "crm.db") -> sqlite3.Connection:
    """
    Copies the on-disk SQLite database into memory.

    Args:
        source_path (str): Path to the existing SQLite DB file.

    Returns:
        sqlite3.Connection: In-memory SQLite connection with copied contents.
    """
    disk_conn = sqlite3.connect(source_path)
    memory_conn = sqlite3.connect(":memory:")
    disk_conn.backup(memory_conn)
    disk_conn.close()
    return memory_conn


@pytest.fixture
def app() -> Flask:
    """
    Create a Flask test app using a fully in-memory copy of `crm.db`.

    Returns:
        Flask: The configured Flask application.
    """
    os.environ["FLASK_ENV"] = "testing"
    app = create_app()
    mem_conn = copy_db_to_memory()

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    with app.app_context():
        # Reflect the schema into SQLAlchemy's engine and copy data
        raw_conn = db.engine.raw_connection()
        # Use driver_connection instead of connection to avoid deprecation warning
        mem_conn.backup(raw_conn.driver_connection)
        yield app
        db.session.remove()


@pytest.fixture
def client(app: Flask):
    """
    Creates a test client for the Flask application.

    Args:
        app: The Flask application fixture.

    Returns:
        A Flask test client.
    """
    return app.test_client()


@pytest.fixture
def test_user(app: Flask) -> User:
    """
    Creates a test admin user (newadmin@example.com) to avoid conflicts.

    Args:
        app: The Flask application fixture.

    Returns:
        User: The created or updated user.
    """
    user = User.query.filter_by(email="newadmin@example.com").first()
    if not user:
        user = User(
            username="newadmin",
            name="Test Admin",
            email="newadmin@example.com",
            password=generate_password_hash("password"),
            is_admin=True,
        )
        db.session.add(user)
    else:
        user.name = "Test Admin"
        user.password_hash = generate_password_hash("password")
        user.is_admin = True
    db.session.commit()
    return user


@pytest.fixture
def logged_in_client(client, test_user):
    """
    Logs in the test admin user (newadmin@example.com).

    Args:
        client: The Flask test client.
        test_user: The test user fixture.

    Returns:
        FlaskClient: The authenticated test client.
    """
    response = client.post(
        "/auth/login",
        data={"email": "newadmin@example.com", "password": "password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    return client