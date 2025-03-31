"""
Unit tests for User model.
"""

import pytest
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.models.user import User
from werkzeug.security import check_password_hash


def test_user_creation(db):
    """Test basic user creation and retrieval."""
    user = User.query.filter_by(email='test@example.com').first()

    assert user is not None
    assert user.email == 'test@example.com'
    assert user.is_active == True
    assert check_password_hash(user.password_hash, 'password123')


def test_user_authentication(db):
    """Test user authentication methods."""
    user = User.query.filter_by(email='test@example.com').first()

    # Test is_authenticated property (should be True for valid users)
    assert user.is_authenticated

    # Test is_active property
    assert user.is_active

    # Test get_id method
    assert user.get_id() == str(user.id)

    # Test inactive user
    inactive_user = User.query.filter_by(email='inactive@example.com').first()
    assert inactive_user.is_active == False


def test_user_representation(db):
    """Test the string representation of User objects."""
    user = User.query.filter_by(email='test@example.com').first()

    # Assuming __repr__ is implemented to include email
    assert 'test@example.com' in repr(user)