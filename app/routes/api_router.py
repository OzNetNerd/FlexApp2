# app/routes/api_router.py

from flask import Flask, Blueprint

from app.routes.api.route_registration import register_api_crud_routes
from app.utils.router_utils import register_blueprint_routes

# Import nested API blueprints
from app.routes.api.companies import companies_api_bp


def register_api_blueprints(app: Flask) -> None:
    """Register API blueprints with their CRUD routes."""

    # Create a root API blueprint
    api_bp = Blueprint("api", __name__, url_prefix="/api")

    # Register nested blueprints with the API blueprint
    api_bp.register_blueprint(companies_api_bp)

    # Register the API blueprint with the app
    app.register_blueprint(api_bp)

    # Continue to use the auto-registration for top-level API blueprints
    register_blueprint_routes(
        app=app,
        package_path="app.routes.api",
        config_suffix="_api_crud_config",
        register_func=register_api_crud_routes,
        blueprint_suffix="_api_bp",
    )