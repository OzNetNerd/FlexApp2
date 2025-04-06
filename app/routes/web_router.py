import logging
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import BaseContext

from app.routes.web.auth import auth_bp
# from app.routes.web.index import index_bp
from app.routes.web.crud.companies import companies_bp
from app.routes.web.crud.contacts import contacts_bp
from app.routes.web.crud.opportunities import opportunities_bp
from app.routes.web.crud.users import users_bp
from app.routes.web.crud.tasks import tasks_bp
from app.routes.blueprint_factory import create_blueprint
from flask import Flask, request

logger = logging.getLogger(__name__)

# Create blueprints for remaining routes that don't have dedicated modules yet
settings_bp = create_blueprint("settings")
relationships_bp = create_blueprint("relationships")
crisp_scores_bp = create_blueprint("crisp_scores")


def register_routes(app: Flask):
    """
    Central routing registration function for the entire application.
    This is the main entry point for all route registration.

    Args:
        app: Flask application instance
    """
    logger.info("Registering all application routes...")

    # Import and register blueprints
    from app.routes import register_blueprints

    register_blueprints(app)

    # Register any ad-hoc routes that don't fit into the blueprint structure
    register_error_handlers(app)
    register_special_routes(app)

    logger.info("All routes registered successfully.")


def register_error_handlers(app: Flask):
    """Register error handlers for the application."""

    @app.errorhandler(404)
    def page_not_found(e):
        context = BaseContext(title="404 Not Found", item=str(e), read_only=True)
        return render_safely("base/errors/404.html", context, "Page not found."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        context = BaseContext(title="500 Internal Server Error", item=str(e), read_only=True)
        return render_safely("base/errors/500.html", context, "Internal server error."), 500

    logger.info("Error handlers registered")


def register_special_routes(app: Flask):
    """Register special routes that don't fit the standard pattern."""
    from flask import jsonify, session as flask_session
    from flask_login import current_user

    @app.route("/")
    def index():
        """Main dashboard/home page."""
        logger.info("Rendering dashboard/home page.")
        context = BaseContext(title="Dashboard", info="")
        fallback_message = "Sorry, we couldn't load the dashboard. Please try again later."
        return render_safely("index.html", context, fallback_message)

    @app.route("/debug-session")
    def debug_session():
        result = {
            "is_authenticated": current_user.is_authenticated,
            "session_keys": list(flask_session.keys()) if flask_session else [],
            "permanent": flask_session.permanent if flask_session else None,
            "user_id": current_user.get_id() if current_user.is_authenticated else None,
            "remember_token": request.cookies.get("remember_token") is not None,
            "cookies": {k: v for k, v in request.cookies.items()},
        }
        return jsonify(result)

    logger.info("Special routes registered")


# Add routes for blueprints that don't follow the standard CRUD pattern
@settings_bp.route("/")
def settings_index():
    """Settings page."""

    context = BaseContext(title="Settings")
    return render_safely("pages/misc/settings.html", context, "Failed to load settings.")


@relationships_bp.route("/")
def relationships_index():
    """Relationships list page."""

    context = BaseContext(title="Relationships")
    return render_safely("pages/tables/relationships.html", context, "Failed to load relationships.")


def register_web_blueprints(app):
    """Register all web blueprints with the Flask application."""
    logger.info("Registering web blueprints...")

    # app.register_blueprint(index_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(relationships_bp)
    app.register_blueprint(crisp_scores_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(settings_bp)

    logger.info("Web blueprints registered successfully.")
