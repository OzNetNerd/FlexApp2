"""
Basic tests for auth routes that don't require database interaction.
Tests only if routes are reachable.
"""

import pytest
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def test_login_get_exists(client):
    """Test that login GET route exists."""
    response = client.get('/auth/login')
    assert response.status_code in [200, 302]


def test_login_post_accepts_data(client):
    """Test that login POST route accepts form data."""
    response = client.post(
        '/auth/login',
        data={
            'email': 'test@example.com',
            'password': 'password123'
        }
    )
    # We don't care about the response code, just that it accepts the POST
    assert response.status_code in [200, 302, 401, 422]  # Any reasonable response


def test_logout_exists(client):
    """Test that logout route exists."""
    response = client.get('/auth/logout')
    assert response.status_code in [200, 302]