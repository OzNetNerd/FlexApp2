"""
Functional tests for authentication flow.
"""

import pytest
from flask import session, url_for


def test_root_url_redirect(client):
    """Test that the root URL redirects to the login page with the 'next' parameter."""
    response = client.get('/', follow_redirects=False)

    assert response.status_code == 302
    assert response.location == 'http://127.0.0.1:5000/auth/login?next=/'


def test_login_to_protected_page(client, db, mock_user):
    """Test the complete login flow from redirect to protected page access."""
    # First, try accessing the main page (assuming it requires login)
    response = client.get('/', follow_redirects=True)

    # Should end up at login page
    assert response.status_code == 200
    assert b'Welcome to CRM' in response.data

    # Now login
    response = client.post(
        '/auth/login?next=/',
        data={
            'email': mock_user['email'],
            'password': 'password123'
        },
        follow_redirects=True
    )

    # Should be redirected to main page after login
    assert response.status_code == 200
    assert b'Logged in successfully' in response.data

    # User should now be in session
    with client.session_transaction() as sess:
        assert '_user_id' in sess


def test_remember_me_functionality(client, db, mock_user):
    """Test that the remember me functionality sets appropriate cookies."""
    response = client.post(
        '/auth/login',
        data={
            'email': mock_user['email'],
            'password': 'password123',
            'remember': '1'
        },
        follow_redirects=True
    )

    # Check response
    assert response.status_code == 200

    # Check for remember cookie
    cookies = [cookie for cookie in client.cookie_jar]
    remember_cookie = next((cookie for cookie in cookies if cookie.name == 'remember_token'), None)

    assert remember_cookie is not None
    assert remember_cookie.expires is not None  # Should have an expiration


def test_session_persistence(client, db, mock_user):
    """Test session persistence after login."""
    # Login
    client.post(
        '/auth/login',
        data={
            'email': mock_user['email'],
            'password': 'password123'
        },
        follow_redirects=True
    )

    # Make another request to verify session persistence
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200

    # User should still be in session
    with client.session_transaction() as sess:
        assert '_user_id' in sess


def test_flash_messages(client, db, mock_user):
    """Test that appropriate flash messages are displayed."""
    # Test successful login flash
    response = client.post(
        '/auth/login',
        data={
            'email': mock_user['email'],
            'password': 'password123'
        },
        follow_redirects=True
    )
    assert b'Logged in successfully' in response.data

    # Test failed login flash
    response = client.post(
        '/auth/login',
        data={
            'email': mock_user['email'],
            'password': 'wrong_password'
        },
        follow_redirects=True
    )
    assert b'Invalid email or password' in response.data

    # Test logout flash (need to login first)
    client.post(
        '/auth/login',
        data={
            'email': mock_user['email'],
            'password': 'password123'
        }
    )
    response = client.get('/auth/logout', follow_redirects=True)
    assert b'Logged out' in response.data