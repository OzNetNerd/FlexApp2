# app/routes/api_router.py

from flask import Flask
from app.utils.app_logging import get_logger
from app.routes.api.route_registration import register_api_crud_routes
from app.utils.router_utils import discover_blueprint_packages
import importlib

logger = get_logger()


def register_api_blueprints(app: Flask) -> None:
    """Register API blueprints with their CRUD routes."""
    logger.info("Registering API blueprints")

    # Discover and register API CRUD routes first (if needed)
    blueprints = discover_blueprint_packages(
        package_path="app.routes.api",
        bp_suffix="_api_bp"
    )

    # Configure routes if needed
    for bp_name, (_, module_path) in blueprints.items():
        if module_path:
            module = importlib.import_module(module_path)
            for attr in dir(module):
                if attr.endswith("_api_crud_config"):
                    config = getattr(module, attr)
                    register_api_crud_routes(config)

    # Register each blueprint directly with the app
    for bp_name, (blueprint, _) in blueprints.items():
        app.register_blueprint(blueprint)