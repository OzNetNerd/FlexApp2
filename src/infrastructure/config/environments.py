"""Environment-specific configuration classes.

This module provides configuration classes for different environments
(development, testing, production) that extend the base configuration.
"""

import os
from typing import Type

from .base import BaseConfig, PROJECT_ROOT


class DevelopmentConfig(BaseConfig):
    """Development environment configuration.

    Configuration settings specific to the development environment.
    Enables debug mode and uses less strict security settings.
    """
    DEBUG = True

    # In development, we use less strict security settings
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

    # Database configuration - uses the default SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{PROJECT_ROOT}/crm.db"
    )


class TestingConfig(BaseConfig):
    """Testing environment configuration.

    Configuration settings specific to the testing environment.
    Uses in-memory SQLite database and enables testing mode.
    """
    TESTING = True
    DEBUG = True

    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # For testing, we disable protection against CSRF
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production environment configuration.

    Configuration settings specific to the production environment.
    Enforces strict security settings and disables debug mode.
    """
    DEBUG = False

    # In production, we enforce strict security settings
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    REMEMBER_COOKIE_SECURE = True  # Requires HTTPS

    # Use environment variable for database connection
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Ensure a strong secret key is set
    SECRET_KEY = os.environ.get("SECRET_KEY")

    @classmethod
    def is_valid(cls) -> bool:
        """Validates that all required configuration values are set.

        Returns:
            bool: True if all required configuration values are set, False otherwise.
        """
        return bool(cls.SECRET_KEY and cls.SQLALCHEMY_DATABASE_URI)


class ConfigFactory:
    """Factory for creating configuration objects based on the environment.

    This class provides methods to get the appropriate configuration class
    based on the current environment setting.
    """

    @staticmethod
    def get_config() -> Type[BaseConfig]:
        """Returns the appropriate configuration class based on the environment.

        Returns:
            Type[BaseConfig]: The configuration class for the current environment.

        Raises:
            ValueError: If an invalid environment is specified.
        """
        env = os.environ.get("FLASK_ENV", "development").lower()

        if env == "development":
            return DevelopmentConfig
        elif env == "testing":
            return TestingConfig
        elif env == "production":
            return ProductionConfig
        else:
            raise ValueError(f"Invalid environment: {env}")