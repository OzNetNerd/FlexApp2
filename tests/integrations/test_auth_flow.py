"""
Functional tests for authentication flow.
"""

import pytest


@pytest.mark.db
@pytest.mark.integration
class TestAuthenticationFlow:
    """Test suite for authentication flow."""

    def test_root_url_redirect(self, client):
        """Test that unauthenticated users are redirected to login."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login?next=/" in response.location

    def test_login_to_protected_page(self, client, mock_user):
        """Test the complete login flow for accessing a protected page."""
        # First access the protected page (redirects to login)
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200

        # Now log in
        response = client.post(
            "/auth/login?next=/",
            data={
                "email": mock_user["email"],
                "password": mock_user["password"],
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_remember_me_functionality(self, client, mock_user):
        """Test the 'remember me' functionality during login."""
        response = client.post(
            "/auth/login",
            data={
                "email": mock_user["email"],
                "password": mock_user["password"],
                "remember": "1"
            },
            follow_redirects=True
        )
        assert response.status_code == 200

    def test_session_persistence(self, client, mock_user):
        """Test that the user's session persists after login."""
        # Log in first
        client.post(
            "/auth/login",
            data={
                "email": mock_user["email"],
                "password": mock_user["password"],
            },
            follow_redirects=True,
        )

        # Now access a protected page
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200