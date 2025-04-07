# web_router.py

import logging
import traceback
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import BaseContext
from flask import Flask, request, Blueprint, jsonify
from flask_login import current_user

from app.routes.web.companies import companies_bp
from app.routes.web.contacts import contacts_bp
from app.routes.web.opportunities import opportunities_bp
from app.routes.web.users import users_bp
from app.routes.web.tasks import tasks_bp
from app.routes.web.settings import settings_bp
from app.routes.web.auth import auth_bp

# Register the blueprint with your Flask app


logger = logging.getLogger(__name__)


# Define blueprints with original names for template compatibility
relationships_bp = Blueprint('relationships', __name__, url_prefix='/relationships')
crisp_scores_bp = Blueprint('crisp_scores', __name__, url_prefix='/crisp_scores')

#
# # Define blueprint routes with blueprint-scoped function names
# @settings_bp.route("/")
# def index():
#     """Settings page."""
#     logger.info(f"📝 Rendering settings page: {request.method} {request.path}")
#     logger.debug(f"📝 Request ID: {id(request)}")
#     context = BaseContext(title="Settings")
#     return render_safely("pages/misc/settings.html", context, "Failed to load settings.")
#
#
# @relationships_bp.route("/")
# def relationships_index():
#     """Relationships list page."""
#     logger.info(f"📝 Rendering relationships page: {request.method} {request.path}")
#     logger.debug(f"📝 Request ID: {id(request)}")
#     context = BaseContext(title="Relationships")
#     return render_safely("pages/tables/relationships.html", context, "Failed to load relationships.")
#
#
# @crisp_scores_bp.route("/")
# def crisp_scores_index():
#     """Crisp scores page."""
#     logger.info(f"📝 Rendering crisp scores page: {request.method} {request.path}")
#     logger.debug(f"📝 Request ID: {id(request)}")
#     context = BaseContext(title="Crisp Scores")
#     return render_safely("pages/tables/crisp_scores.html", context, "Failed to load crisp scores.")
#
#
def register_application_blueprints(app: Flask) -> None:
    """
    Central function for registering all blueprints in the application.

    This function serves as the single point of registration for all blueprints
    in the application. Each blueprint represents a distinct functional area or
    feature set within the application. Adding new blueprints to this function
    will make them available throughout the application.

    Args:
        app (Flask): The Flask application instance to which blueprints will be registered

    Returns:
        None: This function modifies the app in-place and does not return a value

    Example:
        register_application_blueprints(app)
    """
    logger.info("Registering all application blueprints...")

    app.register_blueprint(companies_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)

#     # Add request tracing middleware
#     @app.before_request
#     def log_request_info():
#         logger.info(f"📥 Web Request: {request.method} {request.path}")
#         logger.debug(f"📝 Request ID: {id(request)}")
#         logger.debug(f"📝 Request args: {request.args}")
#         logger.debug(f"📝 Request headers: {dict(request.headers)}")
#         logger.debug(f"📝 Request form: {request.form}")
#
#     @app.after_request
#     def log_response_info(response):
#         logger.info(f"📤 Web Response: {response.status_code} for {request.method} {request.path}")
#         logger.debug(f"📝 Response headers: {dict(response.headers)}")
#         logger.debug(f"📝 Response content type: {response.content_type}")
#         logger.debug(f"📝 Response length: {response.content_length} bytes")
#         return response
#
#     # Step 1: First register special routes and error handlers
#     register_error_handlers(app)
#     register_special_routes(app)
#
#     # Step 2: Register misc blueprints defined in this file
#     register_misc_blueprints(app)
#
#     # Step 3: Register web blueprints from web/__init__.py
#     # But modify the function to exclude blueprints we've already registered
#     from app.routes import register_web_with_exclusions
#     logger.info("Starting web blueprint registration with exclusions")
#     register_web_with_exclusions(app, ['settings', 'relationships', 'crisp_scores'])
#
#     logger.info("All routes registered successfully.")
#
#
# def register_error_handlers(app: Flask):
#     """Register error handlers for the application."""
#
#     @app.errorhandler(404)
#     def page_not_found(e):
#         logger.warning(f"⚠️ 404 error: {request.method} {request.path}")
#         logger.debug(f"📝 Request args: {request.args}")
#         context = BaseContext(title="404 Not Found", item=str(e), read_only=True)
#         return render_safely("base/errors/404.html", context, "Page not found."), 404
#
#     @app.errorhandler(500)
#     def internal_server_error(e):
#         logger.error(f"❌ 500 error: {request.method} {request.path}")
#         logger.error(f"❌ Exception: {str(e)}")
#         logger.error(f"❌ Traceback: {traceback.format_exc()}")
#         context = BaseContext(title="500 Internal Server Error", item=str(e), read_only=True)
#         return render_safely("base/errors/500.html", context, "Internal server error."), 500
#
#     @app.errorhandler(Exception)
#     def handle_unexpected_error(e):
#         logger.error(f"❌ Unhandled exception: {type(e).__name__}: {str(e)}")
#         logger.error(f"❌ Request: {request.method} {request.path}")
#         logger.error(f"❌ Traceback: {traceback.format_exc()}")
#         context = BaseContext(
#             title="Unexpected Error",
#             item=f"{type(e).__name__}: {str(e)}",
#             read_only=True
#         )
#         return render_safely("base/errors/500.html", context, "An unexpected error occurred."), 500
#
#     logger.info("Error handlers registered")
#
#
# def register_special_routes(app: Flask):
#     """Register special routes that don't fit the standard pattern."""
#     from flask import jsonify, session as flask_session
#
#     @app.route("/")
#     def main_index():
#         """Main dashboard/home page."""
#         logger.info(f"📝 Rendering dashboard/home page: {request.method} {request.path}")
#         logger.debug(f"📝 Request ID: {id(request)}")
#         context = BaseContext(title="Dashboard", info="", current_user=current_user, show_navbar=True)
#         fallback_message = "Sorry, we couldn't load the dashboard. Please try again later."
#         return render_safely("index.html", context, fallback_message)
#
#     # @app.route("/debug-session")
#     # def debug_session():
#     #     logger.info(f"📝 Debug session endpoint called: {request.method} {request.path}")
#     #     result = {
#     #         "is_authenticated": current_user.is_authenticated,
#     #         "session_keys": list(flask_session.keys()) if flask_session else [],
#     #         "permanent": flask_session.permanent if flask_session else None,
#     #         "user_id": current_user.get_id() if current_user.is_authenticated else None,
#     #         "remember_token": request.cookies.get("remember_token") is not None,
#     #         "cookies": {k: v for k, v in request.cookies.items()},
#     #     }
#     #     logger.debug(f"📝 Debug session response: {result}")
#     #     return jsonify(result)
#
#     logger.info("Special routes registered")
#
#
# def register_misc_blueprints(app):
#     """Register miscellaneous blueprints."""
#     logger.info(f"Registering blueprint: {settings_bp.name} with url_prefix: {settings_bp.url_prefix}")
#     app.register_blueprint(settings_bp)
#
#     logger.info(f"Registering blueprint: {relationships_bp.name} with url_prefix: {relationships_bp.url_prefix}")
#     app.register_blueprint(relationships_bp)
#
#     logger.info(f"Registering blueprint: {crisp_scores_bp.name} with url_prefix: {crisp_scores_bp.url_prefix}")
#     app.register_blueprint(crisp_scores_bp)
#
#     logger.info("Miscellaneous blueprints registered successfully")