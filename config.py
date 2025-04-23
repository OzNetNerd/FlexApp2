import os
import pathlib

from app.utils.app_logging import get_logger

logger = get_logger()

# Get the absolute path to the root directory
BASE_DIR = pathlib.Path(__file__).parent.absolute()

# Configure logger to ensure it outputs to console
# import logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


# Create a console handler and set level to debug
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.DEBUG)

# Create a formatter and add it to the handler
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# console_handler.setFormatter(formatter)

# Add the handler to the logger
# logger.addHandler(console_handler)

# Log the base directory
# logger.debug(f"Base directory set to: {BASE_DIR}")


class Config:
    """Configuration class to manage app settings."""

    # Basic configuration
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_key_for_development")
    logger.debug(f"SECRET_KEY set to: {SECRET_KEY}")

    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24  # 24 hours in seconds
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True

    # Session cookie settings
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 30  # 30 days
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    REMEMBER_COOKIE_HTTPONLY = True

    # Database configuration: Log the DB URI being used
    if os.environ.get("FLASK_ENV") == "testing":
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Use in-memory SQLite for testing
        logger.debug(f"Using in-memory SQLite DB for testing")
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR}/crm.db")
        logger.debug(f"Using database: {SQLALCHEMY_DATABASE_URI}")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application settings
    APP_NAME = "Flask CRM"
    ITEMS_PER_PAGE = 15

    # Default to development mode unless specified
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    logger.debug(f"DEBUG mode set to: {DEBUG}")
