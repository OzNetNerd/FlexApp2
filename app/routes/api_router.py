# api_router.py

import logging
import traceback
from flask import Flask, request, jsonify
from app.routes.blueprint_factory import create_blueprint

logger = logging.getLogger(__name__)

# Create blueprints for API routes that don't have dedicated modules
misc_api_bp = create_blueprint("misc_api", url_prefix="/api/misc")


def register_api_routes(app: Flask):
    """
    Central API routing registration function for the entire application.
    This handles non-blueprint API functionality.

    Args:
        app: Flask application instance
    """
    logger.info("Registering additional API routes...")

    # Register API error handlers and special routes
    register_api_error_handlers(app)
    register_api_special_routes(app)

    # Add this line to register all API blueprints
    from app.routes.api import register_api_blueprints
    logger.info("Starting API blueprint registration")
    register_api_blueprints(app)
    logger.info("API blueprints registered")

    # Register the misc_api_bp blueprint
    logger.info(f"Registering misc API blueprint: {misc_api_bp.name}")
    app.register_blueprint(misc_api_bp)

    # Add request tracing middleware
    @app.before_request
    def log_request_info():
        if request.path.startswith('/api'):
            logger.info(f"📥 API Request: {request.method} {request.path}")
            logger.debug(f"📝 Request ID: {id(request)}")
            logger.debug(f"📝 Request args: {request.args}")
            logger.debug(f"📝 Request headers: {dict(request.headers)}")
            logger.debug(f"📝 Request JSON: {request.get_json(silent=True)}")
            logger.debug(f"📝 Request form: {request.form}")

    @app.after_request
    def log_response_info(response):
        if request.path.startswith('/api'):
            logger.info(f"📤 API Response: {response.status_code} for {request.method} {request.path}")
            logger.debug(f"📝 Response headers: {dict(response.headers)}")
            logger.debug(f"📝 Response length: {response.content_length} bytes")
            # Don't log response body as it could be large
        return response

    logger.info("Additional API routes registered successfully.")


def register_api_error_handlers(app: Flask):
    """Register API error handlers for the application."""

    @app.errorhandler(404)
    def api_page_not_found(e):
        if request.path.startswith('/api'):
            logger.warning(f"⚠️ API 404 error: {request.method} {request.path}")
            logger.debug(f"📝 Request args: {request.args}")
            return jsonify({"error": "API endpoint not found", "path": request.path}), 404
        return e  # Let the web error handler handle non-API routes

    @app.errorhandler(500)
    def api_internal_server_error(e):
        if request.path.startswith('/api'):
            logger.error(f"❌ API 500 error: {request.method} {request.path}")
            logger.error(f"❌ Exception: {str(e)}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return jsonify({"error": "Internal API error", "details": str(e)}), 500
        return e  # Let the web error handler handle non-API routes

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        if request.path.startswith('/api'):
            logger.error(f"❌ Unhandled API exception: {type(e).__name__}: {str(e)}")
            logger.error(f"❌ Request: {request.method} {request.path}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return jsonify({
                "error": "Unexpected error",
                "type": type(e).__name__,
                "message": str(e)
            }), 500
        return e  # Let the web error handler handle non-API routes

    logger.info("API error handlers registered")


def register_api_special_routes(app: Flask):
    """Register special API routes that don't fit the standard pattern."""

    @app.route("/api/debug")
    def api_debug():
        logger.info(f"📝 API debug endpoint called: {request.method} {request.path}")
        logger.debug(f"📝 Debug request headers: {dict(request.headers)}")
        result = {
            "method": request.method,
            "path": request.path,
            "args": request.args,
            "headers": {k: v for k, v in request.headers.items()},
            "json": request.get_json(silent=True),
        }
        logger.debug(f"📝 Debug response: {result}")
        return jsonify(result)

    logger.info("API special routes registered")


# Add routes for blueprints that don't follow the standard CRUD pattern
@misc_api_bp.route("/")
def misc_index():
    """Miscellaneous API index."""
    logger.info(f"📝 Misc API index called: {request.method} {request.path}")
    return jsonify({"message": "Welcome to the Misc API endpoint"})