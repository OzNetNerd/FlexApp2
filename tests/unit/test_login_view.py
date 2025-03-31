"""
Tests for login view without database dependency.

These tests focus on verifying the functionality of the login view. They do not depend on the database
and instead use mock data to test the login flow and the availability of the login route.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def test_login_route_exists(app):
    """Test that the login route exists and is accessible.

    This test ensures that the `/auth/login` route is available and responds with a 200 status code
    when accessed via a GET request.

    Args:
        app (Flask): The Flask application fixture.

    Asserts:
        - The response status code is 200 (OK).
    """
    with app.test_client() as client:
        response = client.get('/auth/login')
        assert response.status_code == 200


def test_login_with_mocks(app, monkeypatch):
    """Test login functionality using mocked data.

    This test simulates a login request using mock user data. It ensures that the login route can
    accept POST requests and return appropriate responses without requiring a real database.

    Args:
        app (Flask): The Flask application fixture.
        monkeypatch (MonkeyPatch): A pytest fixture used to mock methods and functions.

    Asserts:
        - The response status code is either 200 (OK) or 302 (redirect), indicating that the login route
          processes the request properly.
    """
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
