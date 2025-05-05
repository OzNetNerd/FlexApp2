"""Base configuration module for the application.

This module provides the base configuration class that all environment-specific
configurations inherit from. It defines default settings and configuration methods.
"""

import os
import pathlib
from typing import Any, Dict, Optional

# Get the absolute path to the project root directory (src folder)
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.absolute()


class BaseConfig:
    """Base configuration class with default settings.

    This class provides the foundation for all configuration settings in the application.
    Environment-specific configuration classes should inherit from this class and
    override settings as needed.

    Attributes:
        APP_NAME: The name of the application.
        SECRET_KEY: Secret key for cryptographic functions, should be overridden in production.
        DEBUG: Flag indicating if debug mode is enabled.
        TESTING: Flag indicating if the application is in testing mode.
        LOG_HTTP_REQUESTS: Flag to enable/disable HTTP request logging.

        # Session settings
        SESSION_TYPE: The type of session storage to use.
        SESSION_PERMANENT: Flag indicating if sessions should be permanent.
        SESSION_USE_SIGNER: Flag to enable/disable session signing.
        PERMANENT_SESSION_LIFETIME: Duration of permanent sessions in seconds.
        SESSION_COOKIE_SECURE: Flag to only send cookies over HTTPS.
        SESSION_COOKIE_HTTPONLY: Flag to prevent JavaScript from accessing cookies.
        SESSION_COOKIE_SAMESITE: SameSite policy for cookies.

        # Remember Me cookie settings
        REMEMBER_COOKIE_DURATION: Duration of the remember cookie in seconds.
        REMEMBER_COOKIE_SECURE: Flag to only send remember cookies over HTTPS.
        REMEMBER_COOKIE_HTTPONLY: Flag to prevent JavaScript from accessing remember cookies.

        # Database settings
        SQLALCHEMY_DATABASE_URI: URI for the database connection.
        SQLALCHEMY_TRACK_MODIFICATIONS: Flag to enable/disable SQLAlchemy modification tracking.

        # Application settings
        ITEMS_PER_PAGE: Default number of items to display per page.
    """

    # Basic configuration
    APP_NAME = "Flask CRM"
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_key_for_development")
    DEBUG = False
    TESTING = False
    LOG_HTTP_REQUESTS = False

    # Session configuration
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24  # 24 hours in seconds
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Remember Me cookie settings
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 30  # 30 days
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    REMEMBER_COOKIE_HTTPONLY = True

    # Database configuration
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{PROJECT_ROOT}/crm.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application settings
    ITEMS_PER_PAGE = 15

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Returns a dictionary of configuration values.

        Returns:
            Dict[str, Any]: Configuration dictionary containing all public attributes
                of this class (those not starting with an underscore).
        """
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }