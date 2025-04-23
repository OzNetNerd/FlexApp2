"""
Test that the root URL redirects to the login page for unauthenticated users.

This test ensures that accessing a protected route, such as the root URL (`/`), without being authenticated
properly redirects the user to the login page.
"""

import os
import sys
from unittest.mock import patch

import pytest

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def test_index_redirect_to_login(app):
    """Test that accessing the root URL redirects unauthenticated users to the login page.

    This test simulates accessing the root URL as an unauthenticated user, ensuring that they are
    redirected to the login page with the correct 'next' parameter, indicating where they tried to access.

    Args:
        app (Flask): The Flask application fixture for running the app.

    Asserts:
        - The response status code is 302 (redirect).
        - The Location header contains the login URL with a 'next' parameter set to '/'.
    """
    with app.test_client() as client:
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login?next=/" in response.location
