"""
Basic functional tests for authentication flow.

This file contains simple tests to verify the basic authentication functionality, including
root URL redirection, login page loading, and the logout flow. These tests ensure that the most
fundamental authentication features work as expected.
"""

import pytest

def test_root_url_redirect(client):
    """Test that the root URL redirects unauthenticated users to the login page.

    This test verifies that when an unauthenticated user accesses the root URL, they are
    properly redirected to the login page with a 'next' parameter set to the root URL.

    Args:
        client (FlaskClient): The test client fixture for making requests.

    Asserts:
        - Response status code is 302 (redirect).
        - The Location header contains '/auth/login?next=/'.
    """
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login?next=/' in response.location


def test_login_page_loads(client):
    """Test that the login page loads correctly.

    This test ensures that the login page is rendered properly when a GET request is made
    to the `/auth/login` route.

    Args:
        client (FlaskClient): The test client fixture.

    Asserts:
        - Response status code is 200 (OK).
    """
    response = client.get('/auth/login')
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
    response = client.get('/auth/logout', follow_redirects=False)
    assert response.status_code == 302
