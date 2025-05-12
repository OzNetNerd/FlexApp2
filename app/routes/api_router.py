# app/routes/api_router.py

from flask import Flask, Blueprint
from app.utils.app_logging import get_logger
from app.routes.api.route_registration import register_api_crud_routes
from app.utils.router_utils import register_application_blueprints

logger = get_logger()

def register_api_blueprints(app: Flask) -> None:
    """Register API blueprints with their CRUD routes."""
    logger.info("Registering API blueprints")

    # Create a root API blueprint
    api_bp = Blueprint("api", __name__, url_prefix="/api")

    # Auto-discover and register all API blueprints
    register_application_blueprints(
        app=app,
        package_path="app.routes.api",
        root_blueprint=api_bp,
        config_suffix="_api_crud_config",
        register_func=register_api_crud_routes,
        blueprint_suffix="_api_bp",
    )