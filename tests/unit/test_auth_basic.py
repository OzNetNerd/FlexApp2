"""
Basic tests for authentication routes that don't require database interaction.
These tests verify that the authentication routes are reachable and function as expected.
They test basic functionality like GET and POST requests to the login and logout routes.
"""

import os
import sys

import pytest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def test_login_get_exists(client):
    """Test that the GET method for the login route exists and is reachable.

    This test ensures that the `/auth/login` route responds to a GET request, confirming
    that the login page can be loaded successfully.

    Args:
        client (FlaskClient): The test client fixture.

    Asserts:
        - The response status code is either 200 (OK) or 302 (redirect).
    """
    response = client.get("/auth/login")
    assert response.status_code in [200, 302]


def test_login_post_accepts_data(client):
    """Test that the POST method for the login route accepts form data.

    This test verifies that the `/auth/login` route properly accepts POST requests with login
    data (email and password). It checks that the form submission is processed, regardless of
    whether the login is successful or not.

    Args:
        client (FlaskClient): The test client fixture.

    Asserts:
        - The response status code is one of 200, 302, 401, or 422, indicating that the route
          accepts the POST data and returns an appropriate response.
    """
    response = client.post("/auth/login", data={"email": "test@example.com", "password": "password123"})
    # We don't care about the response code, just that it accepts the POST
    assert response.status_code in [200, 302, 401, 422]  # Any reasonable response


def test_logout_exists(client):
    """Test that the logout route exists and is reachable.

    This test checks that the `/auth/logout` route responds to a GET request, confirming
    that the logout functionality is accessible.

    Args:
        client (FlaskClient): The test client fixture.

    Asserts:
        - The response status code is either 200 (OK) or 302 (redirect).
    """
    response = client.get("/auth/logout")
    assert response.status_code in [200, 302]
