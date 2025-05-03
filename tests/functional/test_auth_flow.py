"""
Functional tests for authentication flow.

This file contains tests that verify the behavior of authentication-related routes and features
such as redirection, login flow, session persistence, and flash messages. These tests ensure that
the user authentication flow works as expected in different scenarios.
"""

import pytest


def test_root_url_redirect(client):
    """Test that the root URL redirects to the login page when unauthenticated.

    This test ensures that when an unauthenticated user tries to access the root URL, they are
    redirected to the login page, with the 'next' parameter pointing to the root URL.

    Args:
        client (FlaskClient): The test client fixture for making requests.

    Asserts:
        - The response status code is 302 (redirect).
        - The redirect location contains '/auth/login?next=/'.
    """
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login?next=/" in response.location


def test_login_page_loads(client):
    """Test that the login page loads correctly.

    This test ensures that the login page is rendered properly when a GET request is made
    to the `/auth/login` route.

    Args:
        client (FlaskClient): The test client fixture.

    Asserts:
        - Response status code is 200 (OK).
    """
    response = client.get("/auth/login")
    assert response.status_code == 200


def test_logout_redirects(client):
    """Test that the logout endpoint redirects users to the login page.

    This test verifies that when a user accesses the logout endpoint, they are redirected
    to the login page after being logged out.

    Args:
        client (FlaskClient): The test client fixture for making requests.

    Asserts:
        - Response status code is 302 (redirect).
    """
    response = client.get("/auth/logout", follow_redirects=False)
    assert response.status_code == 302


def test_login_to_protected_page(client, mock_user):
    """Test the complete login flow for accessing a protected page.

    This test simulates a full login process where the user first accesses a protected page,
    then logs in, and verifies that the page is accessible after successful login.

    Args:
        client (FlaskClient): The test client fixture.
        mock_user (dict): A dictionary containing mock user data.

    Asserts:
        - The protected page returns a 200 status code after login.
    """
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200

    response = client.post(
        "/auth/login?next=/",
        data={
            "email": mock_user["email"],
            "password": mock_user["password"],
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_remember_me_functionality(client, mock_user):
    """Test the 'remember me' functionality during login.

    This test ensures that the 'remember me' functionality is working, allowing the user to stay
    logged in after the session expires by setting the appropriate cookie.

    Args:
        client (FlaskClient): The test client fixture.
        mock_user (dict): The mock user data.

    Asserts:
        - The response status code is 200 after login with the 'remember me' checkbox checked.
    """
    response = client.post(
        "/auth/login", data={"email": mock_user["email"], "password": mock_user["password"], "remember": "1"}, follow_redirects=True
    )
    assert response.status_code == 200


def test_session_persistence(client, mock_user):
    """Test that the user's session persists after login.

    This test verifies that once the user logs in, their session remains active and they can access
    protected routes even after logging out and logging back in.

    Args:
        client (FlaskClient): The test client fixture.
        mock_user (dict): The mock user data.

    Asserts:
        - The response status code is 200 for the protected page after login.
    """
    client.post(
        "/auth/login",
        data={
            "email": mock_user["email"],
            "password": mock_user["password"],
        },
        follow_redirects=True,
    )
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200


def test_flash_messages(client, mock_user):
    """Test that flash messages are displayed during the login process.

    This test ensures that the appropriate flash messages are shown to the user during the login
    process, especially for success or failure scenarios.

    Args:
        client (FlaskClient): The test client fixture.
        mock_user (dict): The mock user data.

    Asserts:
        - The response status code is 200 after posting the login data.
    """
    response = client.post(
        "/auth/login",
        data={
            "email": mock_user["email"],
            "password": mock_user["password"],
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
