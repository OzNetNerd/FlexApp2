"""
Simple unit tests for auth routes.
These tests focus only on route existence and basic functionality.
"""

import pytest
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def test_login_route_exists(client):
    """Test that the login route exists and returns a response."""
    response = client.get('/auth/login')
    assert response.status_code in [200, 302]


def test_login_post_endpoint(client):
    """Test that the login POST endpoint exists."""
    response = client.post(
        '/auth/login',
        data={
            'email': 'test@example.com',
            'password': 'password123'
        }
    )
    # Just checking that it accepts the POST request
    assert response.status_code in [200, 302, 401, 422]


def test_logout_route_exists(client):
    """Test that the logout route exists."""
    response = client.get('/auth/logout')
    assert response.status_code in [200, 302]