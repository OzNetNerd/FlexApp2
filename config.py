import os
import pathlib
import logging

# Get the absolute path to the root directory
BASE_DIR = pathlib.Path(__file__).parent.absolute()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Log the base directory
logger.debug(f"Base directory set to: {BASE_DIR}")


class Config:
    # Basic configuration
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_key_for_development")
    logger.debug(f"SECRET_KEY set to: {SECRET_KEY}")

    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24  # 24 hours in seconds
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True

    # Add to your Config class
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 30  # 30 days
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    REMEMBER_COOKIE_HTTPONLY = True

    # Database configuration
    # Use absolute path to ensure database is created in the correct location
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR}/crm.db"
    )
    logger.debug(f"SQLALCHEMY_DATABASE_URI set to: {SQLALCHEMY_DATABASE_URI}")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application settings
    APP_NAME = "Flask CRM"
    ITEMS_PER_PAGE = 15

    # Default to development mode unless specified
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    logger.debug(f"DEBUG mode set to: {DEBUG}")
