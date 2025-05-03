"""
Simple unit tests for authentication routes.
These tests focus only on route existence and basic functionality.
They verify that the authentication routes are reachable and respond appropriately to basic requests.
"""

import os
import sys

import pytest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def test_login_route_exists(client):
    """Test that the login route exists and returns an appropriate response.

    This test ensures that the `/auth/login` route can be accessed via a GET request and returns
    either a 200 (OK) or 302 (redirect) status code, indicating that the route is properly set up.

    Args:
        client (FlaskClient): The test client fixture for making requests.

    Asserts:
        - The response status code is either 200 (OK) or 302 (redirect).
    """
    response = client.get("/auth/login")
    assert response.status_code in [200, 302]


def test_login_post_endpoint(client):
    """Test that the login POST endpoint accepts form data.

    This test checks that the `/auth/login` route accepts POST requests and processes login data,
    even if the login is not successful. The test ensures that the route exists and can handle form submissions.

    Args:
        client (FlaskClient): The test client fixture for making requests.

    Asserts:
        - The response status code is one of 200, 302, 401, or 422, depending on the request handling.
    """
    response = client.post("/auth/login", data={"email": "test@example.com", "password": "password123"})
    # Just checking that it accepts the POST request
    assert response.status_code in [200, 302, 401, 422]


def test_logout_route_exists(client):
    """Test that the logout route exists and is reachable.

    This test ensures that the `/auth/logout` route can be accessed via a GET request and that it
    returns either a 200 (OK) or 302 (redirect) status code, indicating that the logout functionality
    is properly set up.

    Args:
        client (FlaskClient): The test client fixture for making requests.

    Asserts:
        - The response status code is either 200 (OK) or 302 (redirect).
    """
    response = client.get("/auth/logout")
    assert response.status_code in [200, 302]
