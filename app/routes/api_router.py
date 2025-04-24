# app/routes/api_router.py

from flask import Flask

from app.routes.api.route_registration import register_api_crud_routes
from app.utils.router_utils import register_blueprint_routes


def register_api_blueprints(app: Flask) -> None:
    """Auto-register API blueprints with their CRUD routes."""
    register_blueprint_routes(
        app=app,
        package_path="app.routes.api",
        config_suffix="_api_crud_config",
        register_func=register_api_crud_routes,
        blueprint_suffix="_api_bp"
    )