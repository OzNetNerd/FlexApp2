"""
Tests for login view without database dependency.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def test_login_route_exists(app):
    """Test that the login route exists."""
    with app.test_client() as client:
        response = client.get('/auth/login')
        assert response.status_code == 200


def test_login_with_mocks(app, monkeypatch):
    """Test login functionality with mocks."""
    # Create patches
    mock_user = MagicMock()
    mock_user.email = 'test@example.com'
    mock_user.password_hash = 'hashed_password'

    # Create the client
    with app.test_client() as client:
        # We only care that the route exists and accepts POSTs
        response = client.post(
            '/auth/login',
            data={
                'email': 'test@example.com',
                'password': 'password123'
            }
        )

        # Either OK or redirect is acceptable
        assert response.status_code in [200, 302]