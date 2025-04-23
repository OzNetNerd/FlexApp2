# app/app.py

import logging
from datetime import datetime
from logging import StreamHandler, Formatter, INFO
from typing import Type

from flask import Flask, request, redirect, url_for, make_response, current_app
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from app.utils.app_logging import get_logger
from config import Config
from app.models.base import db
from app.models import User, Setting
from app.routes.api_router import register_api_blueprints
from app.routes.web_router import register_web_blueprints
from app.routes.web.components.template_renderer import handle_template_error

logger = get_logger()

login_manager = LoginManager()
migrate = Migrate()


@login_manager.unauthorized_handler
def unauthorized() -> "flask.wrappers.Response":
    """Handle unauthorized access attempts."""
    return make_response("🔒 Unauthorized - Please log in first", 401)


def create_app(config_class: Type[Config] = Config) -> Flask:
    """Initialize and configure the Flask application.

    Args:
        config_class (Type[Config]): Configuration class to load.

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(config_class)

    app.config.update(
        PERMANENT_SESSION_LIFETIME=60 * 60 * 24,  # 1 day
        SESSION_PERMANENT=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE="Lax",
        REMEMBER_COOKIE_DURATION=60 * 60 * 24 * 30,  # 30 days
        REMEMBER_COOKIE_HTTPONLY=True,
    )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth_bp.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # --- Configure console logging at INFO level -----------------
    console_handler = StreamHandler()
    console_handler.setLevel(INFO)
    console_handler.setFormatter(Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root_logger = logging.getLogger()
    root_logger.setLevel(INFO)
    root_logger.addHandler(console_handler)
    logger.info("Configured console logging at INFO level")
    # ------------------------------------------------------------

    @app.errorhandler(TypeError)
    def handle_type_error(e: TypeError):
        """Render a friendly error page when a TypeError occurs."""
        logger.error(f"TypeError: {e}")
        return handle_template_error(e, request.endpoint or "", request.path, "An error occurred while preparing the page context")

    @login_manager.user_loader
    def load_user(user_id: str):
        """Load a user by ID for session management."""
        logger.debug(f"Loading user with ID: {user_id}")
        return db.session.get(User, int(user_id))

    # Register routes
    logger.info("Registering API routes")
    register_api_blueprints(app)
    logger.info("Registering application blueprints")
    register_web_blueprints(app)

    @app.before_request
    def log_request():
        """Log each incoming HTTP request."""
        request_id = getattr(request, "id", hex(id(request))[2:])
        logger.info(f"[{request_id}] {request.method} {request.path} from {request.remote_addr}")

    @app.before_request
    def require_login():
        """Enforce login for non-whitelisted endpoints."""
        whitelisted = {"auth_bp.login", "auth_bp.logout", "static", "debug_session"}
        endpoint = request.endpoint or ""
        logger.info(f"require_login: endpoint={endpoint}, authenticated={current_user.is_authenticated}")
        if not current_user.is_authenticated:
            if endpoint in whitelisted or endpoint.startswith("static") or endpoint.startswith("api_") or endpoint.endswith(".data"):
                logger.info(f"Access allowed to {endpoint}")
                return None
            logger.info(f"Access denied to {endpoint}; redirecting to login")
            return redirect(url_for("auth_bp.login", next=request.path))

    @app.context_processor
    def inject_globals():
        """Inject common variables into every template context."""
        return {
            "now": datetime.utcnow(),
            "logger": logger,
            "current_app": current_app,
            "is_debug_mode": app.debug,
        }

    with app.app_context():
        logger.info("Seeding settings and creating database tables.")
        Setting.seed()
        db.create_all()

    logger.info("Application initialization complete")
    return app


# Entrypoint
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
