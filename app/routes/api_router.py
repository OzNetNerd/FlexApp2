import logging
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
    register_api_blueprints(app)

    # Register the misc_api_bp blueprint
    app.register_blueprint(misc_api_bp)

    logger.info("Additional API routes registered successfully.")


def register_api_error_handlers(app: Flask):
    """Register API error handlers for the application."""

    @app.errorhandler(404)
    def api_page_not_found(e):
        return jsonify({"error": "API endpoint not found"}), 404

    @app.errorhandler(500)
    def api_internal_server_error(e):
        return jsonify({"error": "Internal API error"}), 500

    logger.info("API error handlers registered")


def register_api_special_routes(app: Flask):
    """Register special API routes that don't fit the standard pattern."""

    @app.route("/api/debug")
    def api_debug():
        result = {
            "method": request.method,
            "args": request.args,
            "json": request.get_json(),
        }
        return jsonify(result)

    logger.info("API special routes registered")


# Add routes for blueprints that don't follow the standard CRUD pattern
@misc_api_bp.route("/")
def misc_index():
    """Miscellaneous API index."""
    return jsonify({"message": "Welcome to the Misc API endpoint"})