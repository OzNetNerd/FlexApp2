# src/infrastructure/auth/user_loader.py

"""
User authentication utilities.

This module provides functions for loading users and managing authentication.
"""

from flask import make_response

from src.infrastructure.flask.extensions import db, login_manager
from src.domain.user.entities import User
from src.infrastructure.logging import get_logger

logger = get_logger()


def configure_user_loader():
    """Configure the user loader for Flask-Login."""

    @login_manager.user_loader
    def load_user(user_id):
        """
        Load a user by ID for session management.

        Args:
            user_id (str): The user ID from the session.

        Returns:
            User: The loaded user object or None if not found.
        """
        logger.debug(f"Loading user with ID: {user_id}")
        return db.session.get(User, int(user_id))
