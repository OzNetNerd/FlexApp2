"""Test configuration fixtures and utilities.

This module provides pytest fixtures and utility functions for testing the FlexApp application,
including database setup, application creation, and authentication helpers.
"""

import os
import pytest
from flask import Flask
from app.app import create_app
from app.models.base import db
from app.models.user import User
from werkzeug.security import generate_password_hash

# Global test credentials
TEST_USER_EMAIL = "newadmin@example.com"
TEST_USER_PASSWORD = "password"
TEST_USER_NAME = "Administrator"  # Expected display name in the navbar
TEST_USERNAME = "newadmin"


@pytest.fixture
def app() -> Flask:
    """
    Create a Flask test app with an in-memory database populated with static test data.

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
        # Create all tables
        db.create_all()

        # -----------------------
        # Populate Static Test Data
        # -----------------------

        # Create test admin user
        test_user = User.query.filter_by(email=TEST_USER_EMAIL).first()
        if not test_user:
            test_user = User(
                username=TEST_USERNAME,
                name=TEST_USER_NAME,
                email=TEST_USER_EMAIL,
                password=generate_password_hash(TEST_USER_PASSWORD),
                is_admin=True,
            )
            db.session.add(test_user)
        else:
            test_user.name = TEST_USER_NAME
            test_user.password_hash = generate_password_hash(TEST_USER_PASSWORD)
            test_user.is_admin = True

        # Create a test company
        from app.models.company import Company
        test_company = Company.query.first()
        if not test_company:
            test_company = Company(
                name="Company 1",
                description="Description of Company 1"
            )
            db.session.add(test_company)
        else:
            test_company.name = "Company 1"
            test_company.description = "Description of Company 1"

        # Create a test contact for the company
        from app.models.contact import Contact
        test_contact = Contact.query.first()
        if not test_contact:
            test_contact = Contact(
                first_name="John",
                last_name="Doe",
                email="johndoe@example.com",
                phone="555-1234",
                company=test_company
            )
            db.session.add(test_contact)

        # Create a test opportunity for the company
        from app.models.opportunity import Opportunity
        test_opportunity = Opportunity.query.first()
        if not test_opportunity:
            test_opportunity = Opportunity(
                name="Opportunity 1",
                description="Opportunity description",
                status="New",
                stage="Prospecting",
                value=10000.0,
                company_id=test_company.id
            )
            db.session.add(test_opportunity)

        # Create a test task associated with the company
        from app.models.task import Task
        test_task = Task.query.first()
        if not test_task:
            test_task = Task(
                title="Follow up",
                description="Follow up with client",
                status="Pending",
                priority="High",
                notable_type="Company",
                notable_id=test_company.id
            )
            db.session.add(test_task)

        db.session.commit()
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
    Retrieves the test admin user from the populated database.

    Args:
        app: The Flask application fixture.

    Returns:
        User: The test admin user.
    """
    with app.app_context():
        return User.query.filter_by(email=TEST_USER_EMAIL).first()


@pytest.fixture
def logged_in_client(client, test_user):
    """
    Logs in the test admin user.

    Args:
        client: The Flask test client.
        test_user: The test user fixture.

    Returns:
        FlaskClient: The authenticated test client.
    """
    response = client.post(
        "/auth/login",
        data={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        follow_redirects=True,
    )
    assert response.status_code == 200
    return client
