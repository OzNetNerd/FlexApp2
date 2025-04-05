import logging
from datetime import datetime
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    session as flask_session,
    make_response,
)
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from config import Config
from app.models.base import db
from app.models import User, Setting
from app.routes.router import register_routes

# ---------------------------------------------
# Logging
# ---------------------------------------------


class IndentationPreservingFormatter(logging.Formatter):
    """Formatter that preserves leading whitespace by re-injecting it after log formatting."""

    def __init__(self, fmt=None, datefmt=None, style="%"):
        super().__init__(fmt, datefmt, style)
        self.indent_level = 0
        self.indent_char = "  "

    def format(self, record):
        original_msg = record.getMessage()

        # Add indentation to the message if needed
        if hasattr(record, "indent_level"):
            indent_level = record.indent_level
        else:
            indent_level = self.indent_level

        # Save leading whitespace (if any)
        leading_ws = ""
        if isinstance(record.msg, str):
            stripped = record.msg.lstrip()
            leading_ws = record.msg[: len(record.msg) - len(stripped)]
            # Add indentation
            if not leading_ws.startswith(self.indent_char * indent_level):
                record.msg = self.indent_char * indent_level + record.msg

        # Format the record using the base logic
        formatted = super().format(record)

        return formatted


def configure_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    handler = logging.StreamHandler()
    formatter = IndentationPreservingFormatter(
        "%(asctime)s - %(name)s - %(filename)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Add indentation control methods to the logger
    def increase_indent():
        formatter.indent_level += 1

    def decrease_indent():
        if formatter.indent_level > 0:
            formatter.indent_level -= 1

    def set_indent(level):
        formatter.indent_level = max(0, level)

    logger.increase_indent = increase_indent
    logger.decrease_indent = decrease_indent
    logger.set_indent = set_indent


# ---------------------------------------------
# Flask Extensions
# ---------------------------------------------

logger = logging.getLogger(__name__)
login_manager = LoginManager()
migrate = Migrate()


@login_manager.unauthorized_handler
def unauthorized():
    return make_response("🔒 Unauthorized - Please log in first", 401)


# ---------------------------------------------
# App Factory
# ---------------------------------------------


def create_app(config_class=Config):
    configure_logging()

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

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth_bp.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.before_request
    def require_login():
        whitelisted = [
            "auth_bp.login",
            "auth_bp.logout",
            "static",
            "debug_session",
        ]
        endpoint = request.endpoint
        if endpoint is None:
            return
        if not current_user.is_authenticated:
            if endpoint in whitelisted or endpoint.startswith("static") or endpoint.startswith("api_") or endpoint.endswith(".data"):
                return
            return redirect(url_for("auth_bp.login", next=request.path))

    # Register all routes
    register_routes(app)

    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow()}

    # Create all tables and seed known app settings
    with app.app_context():
        from app import models  # Ensure all models are loaded

        Setting.seed()
        db.create_all()

    return app


# ---------------------------------------------
# Entrypoint
# ---------------------------------------------

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)