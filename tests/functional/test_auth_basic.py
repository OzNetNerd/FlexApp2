"""
Basic tests for authentication routes that don't require database interaction.
"""

import pytest


class TestAuthRoutes:
    """Test suite for basic authentication route functionality."""

    def test_login_get_exists(self, client):
        """Test that the GET method for the login route exists and is reachable."""
        response = client.get("/auth/login")
        assert response.status_code in [200, 302]

    def test_login_post_accepts_data(self, client):
        """Test that the POST method for the login route accepts form data."""
        response = client.post("/auth/login", data={"email": "test@example.com", "password": "password123"})
        assert response.status_code in [200, 302, 401, 422]

    def test_logout_exists(self, client):
        """Test that the logout route exists and is reachable."""
        response = client.get("/auth/logout")
        assert response.status_code in [200, 302]
