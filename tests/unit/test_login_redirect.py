"""
Test that the root URL redirects to login properly.
"""

import pytest
from unittest.mock import patch
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def test_index_redirect_to_login(app):
    """Test that accessing a protected URL without auth redirects to login."""
    with app.test_client() as client:
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login?next=/' in response.location