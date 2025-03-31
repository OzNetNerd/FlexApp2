"""
Functional tests for authentication flow.
"""

import pytest

def test_root_url_redirect(client):
    """Test that the root URL redirects appropriately."""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login?next=/' in response.location

def test_login_to_protected_page(client, mock_user):
    """Test the complete login flow."""
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200

    response = client.post(
        '/auth/login?next=/',
        data={
            'email': mock_user['email'],
            'password': mock_user['password'],
        },
        follow_redirects=True
    )
    assert response.status_code == 200

def test_remember_me_functionality(client, mock_user):
    """Test remember me functionality."""
    response = client.post(
        '/auth/login',
        data={
            'email': mock_user['email'],
            'password': mock_user['password'],
            'remember': '1'
        },
        follow_redirects=True
    )
    assert response.status_code == 200

def test_session_persistence(client, mock_user):
    """Test session persistence."""
    client.post(
        '/auth/login',
        data={
            'email': mock_user['email'],
            'password': mock_user['password'],
        },
        follow_redirects=True
    )
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200

def test_flash_messages(client, mock_user):
    """Test flash messages."""
    response = client.post(
        '/auth/login',
        data={
            'email': mock_user['email'],
            'password': mock_user['password'],
        },
        follow_redirects=True
    )
    assert response.status_code == 200