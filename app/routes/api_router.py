import logging
from flask import Flask, request, jsonify
from app.routes.blueprint_factory import create_blueprint

logger = logging.getLogger(__name__)

# Import API blueprints that have dedicated modules
from app.routes.api.companies import companies_api_bp
from app.routes.api.contacts import contacts_api_bp
from app.routes.api.opportunities import opportunities_api_bp
from app.routes.api.users import users_api_bp
from app.routes.api.tasks import tasks_api_bp
from app.routes.api.search import search_api_bp
from app.routes.api.generic import generic_api_bp

# Create blueprints for remaining API routes that don't have dedicated modules yet
misc_api_bp = create_blueprint("misc_api", url_prefix="/api/misc")


def register_api_routes(app: Flask):
    """
    Central API routing registration function for the entire application.
    This is the main entry point for all API route registration.

    Args:
        app: Flask application instance
    """
    logger.info("Registering all API routes...")

    # Import and register blueprints
    register_api_blueprints(app)

    # Register any ad-hoc API routes that don't fit into the blueprint structure
    register_api_error_handlers(app)
    register_api_special_routes(app)

    logger.info("All API routes registered successfully.")


def register_api_error_handlers(app: Flask):
    """Register API error handlers for the application."""
    @app.errorhandler(404)
    def api_page_not_found(e):
        return jsonify({"error": "API endpoint not found"}), 404

    @app.errorhandler(500)
    def api_internal_server_error(e):
        return jsonify({"error": "Internal API error"}), 500

    logger.debug("API error handlers registered")


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

    logger.debug("API special routes registered")


# Add routes for blueprints that don't follow the standard CRUD pattern
@misc_api_bp.route("/")
def misc_index():
    """Miscellaneous API index."""
    return jsonify({"message": "Welcome to the Misc API endpoint"})


def register_api_blueprints(app: Flask):
    """Register all API blueprints with the Flask application."""
    logger.debug("Registering API blueprints...")

    app.register_blueprint(companies_api_bp)
    app.register_blueprint(contacts_api_bp)
    app.register_blueprint(opportunities_api_bp)
    app.register_blueprint(users_api_bp)
    app.register_blueprint(tasks_api_bp)
    app.register_blueprint(search_api_bp)
    app.register_blueprint(generic_api_bp)
    app.register_blueprint(misc_api_bp)

    logger.debug("API blueprints registered successfully.")
