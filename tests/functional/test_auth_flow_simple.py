"""
Basic functional tests for authentication flow.
"""

import pytest

def test_root_url_redirect(client):
    """Test that the root URL redirects appropriately."""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login?next=/' in response.location

def test_login_page_loads(client):
    """Test that the login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_logout_redirects(client):
    """Test that the logout endpoint redirects to login."""
    response = client.get('/auth/logout', follow_redirects=False)
    assert response.status_code == 302