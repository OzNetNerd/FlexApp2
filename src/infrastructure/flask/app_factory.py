"""Flask application factory module.

This module provides functions to create and configure the Flask application
with all necessary extensions, middleware, routes, and error handlers.
"""

import logging
from typing import Dict, Any, Optional, Type

from flask import Flask, make_response
from werkzeug.routing import Rule

from src.infrastructure.config import ConfigFactory
from src.infrastructure.flask.extensions import db, login_manager, migrate
from src.infrastructure.flask.middleware import register_middleware
from src.infrastructure.flask.template_utils import register_template_utils
from src.infrastructure.flask.error_handlers import register_error_handlers
from src.infrastructure.logging import configure_logging, get_logger
from src.interfaces.api import register_api_blueprints
from src.interfaces.web import register_web_blueprints
from src.interfaces.graphql import init_graphql
from src.domain.shared.constants import NAVBAR_ENTRIES
from src.infrastructure.persistence.seeders import seed_database

logger = get_logger(__name__)


class CustomRule(Rule):
    """Custom URL routing rule that disables strict slashes by default.

    This class extends the Werkzeug Rule class to provide a more
    flexible URL routing system that doesn't require exact slash
    matching by default.
    """

    def __init__(self, *args, **kwargs):
        """Initialize with strict_slashes disabled by default.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        kwargs.setdefault("strict_slashes", False)
        super().__init__(*args, **kwargs)


def create_app(config_override: Optional[Dict[str, Any]] = None) -> Flask:
    """Initialize and configure the Flask application.

    Creates a new Flask application instance, configures it with the
    appropriate settings based on the current environment, and sets up
    all necessary components.

    Args:
        config_override: Optional dictionary of configuration values to override.
            Useful for testing with specific configurations.

    Returns:
        Flask: The configured Flask application instance ready to run.
    """
    # Create the Flask application
    config_class = ConfigFactory.get_config()
    app_name = config_class.APP_NAME

    logger.debug(f"Creating Flask application: {app_name}")
    app = Flask(app_name, static_folder="static", static_url_path="/static")
    app.url_rule_class = CustomRule
    app.url_map.strict_slashes = False

    # Load configuration
    logger.debug("Loading application configuration")
    app.config.from_object(config_class)

    # Apply any configuration overrides
    if config_override:
        logger.debug("Applying configuration overrides")
        app.config.update(config_override)

    # Configure session settings
    _configure_session_settings(app)

    # Configure logging
    configure_logging(app.name)

    # Disable werkzeug logging if not needed
    if not app.config.get("LOG_HTTP_REQUESTS", False):
        logging.getLogger("werkzeug").setLevel(logging.WARNING)

    # Initialize extensions
    logger.debug("Initializing Flask extensions")
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configure login manager
    _configure_login_manager(login_manager)

    # Initialize GraphQL
    logger.debug("Initializing GraphQL")
    init_graphql(app)

    # Register template utilities (globals, filters, context processors)
    logger.debug("Registering template utilities")
    register_template_utils(app, NAVBAR_ENTRIES)

    # Register error handlers
    logger.debug("Registering error handlers")
    register_error_handlers(app)

    # Register middleware
    logger.debug("Registering middleware")
    register_middleware(app)

    # Register routes
    logger.debug("Registering blueprints")
    register_api_blueprints(app)
    register_web_blueprints(app)

    # Seed database
    logger.info("Application initialization complete, seeding database")
    with app.app_context():
        seed_database()

    logger.info(f"Application {app_name} initialized in {app.config.get('FLASK_ENV', 'development')} mode")
    return app


def _configure_session_settings(app: Flask) -> None:
    """Configure secure session settings for the application.

    Sets appropriate security-related session and cookie settings
    to ensure secure user sessions.

    Args:
        app: Flask application instance.
    """
    # Get values from config with fallbacks to secure defaults
    session_cookie_secure = app.config.get("SESSION_COOKIE_SECURE", True)
    remember_cookie_secure = app.config.get("REMEMBER_COOKIE_SECURE", True)

    app.config.update(
        PERMANENT_SESSION_LIFETIME=app.config.get("PERMANENT_SESSION_LIFETIME", 60 * 60 * 24),  # 1 day
        SESSION_PERMANENT=app.config.get("SESSION_PERMANENT", True),
        SESSION_COOKIE_HTTPONLY=app.config.get("SESSION_COOKIE_HTTPONLY", True),
        SESSION_COOKIE_SECURE=session_cookie_secure,
        SESSION_COOKIE_SAMESITE=app.config.get("SESSION_COOKIE_SAMESITE", "Lax"),
        REMEMBER_COOKIE_DURATION=app.config.get("REMEMBER_COOKIE_DURATION", 60 * 60 * 24 * 30),  # 30 days
        REMEMBER_COOKIE_HTTPONLY=app.config.get("REMEMBER_COOKIE_HTTPONLY", True),
        REMEMBER_COOKIE_SECURE=remember_cookie_secure,
    )

    logger.debug("Session settings configured")


def _configure_login_manager(login_mgr) -> None:
    """Configure the Flask-Login manager.

    Sets up the login manager with appropriate views and message settings
    for handling authentication.

    Args:
        login_mgr: Flask-Login LoginManager instance.
    """
    login_mgr.login_view = "auth_bp.login"
    login_mgr.login_message = "Please log in to access this page."
    login_mgr.login_message_category = "info"

    logger.debug(f"Login manager configured with login view: {login_mgr.login_view}")

    @login_mgr.unauthorized_handler
    def unauthorized():
        """Handle unauthorized access attempts.

        Returns:
            Response: A 401 Unauthorized response with a message.
        """
        return make_response("🔒 Unauthorized - Please log in first", 401)