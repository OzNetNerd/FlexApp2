"""
Unit tests for auth routes.
"""

import pytest
from flask import url_for, session
from unittest.mock import patch, MagicMock
from werkzeug.security import check_password_hash
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.user import User


def test_login_get(client):
    """Test GET request to login route."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Welcome to CRM' in response.data
    assert b'Please sign in to continue' in response.data


def test_login_post_valid(client, db, mock_user):
    """Test successful login with valid credentials."""
    response = client.post(
        '/auth/login',
        data={
            'email': mock_user['email'],
            'password': 'password123'
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b'Logged in successfully' in response.data


def test_login_post_invalid_password(client, db, mock_user):
    """Test login failure with invalid password."""
    response = client.post(
        '/auth/login',
        data={
            'email': mock_user['email'],
            'password': 'wrong_password'
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_login_post_invalid_email(client, db):
    """Test login failure with non-existent email."""
    response = client.post(
        '/auth/login',
        data={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_login_post_with_next(client, db, mock_user):
    """Test login with next parameter in query string."""
    response = client.post(
        '/auth/login?next=/dashboard',
        data={
            'email': mock_user['email'],
            'password': 'password123'
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    # Check if redirected to dashboard (mock the dashboard route for complete testing)


def test_login_inactive_user(client, db):
    """Test login with inactive user account."""
    response = client.post(
        '/auth/login',
        data={
            'email': 'inactive@example.com',
            'password': 'inactivepass'
        },
        follow_redirects=True
    )

    # Assuming inactive users can't log in
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_logout(auth_client):
    """Test the logout functionality."""
    response = auth_client.get('/auth/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b'Logged out' in response.data

    # Check that session doesn't have user info
    with auth_client.session_transaction() as session:
        assert '_user_id' not in session