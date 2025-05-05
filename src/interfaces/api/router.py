# src/interfaces/api/router.py

from typing import Callable, List, Optional

from flask import Flask

from src.interfaces.api.crud_routes import register_api_crud_routes
from src.infrastructure.utils.router_utils import register_blueprint_routes


def register_api_blueprints(
        app: Flask,
        package_path: str = "src.interfaces.api.routes",
        exclusions: Optional[List[str]] = None
) -> None:
    """Register API blueprints with their CRUD routes automatically.

    This function scans the specified package for modules containing API
    blueprint configurations and registers them with the Flask application.

    Args:
        app: The Flask application instance
        package_path: The package path to scan for blueprint modules
        exclusions: Optional list of module names to exclude from registration

    Returns:
        None
    """
    register_blueprint_routes(
        app=app,
        package_path=package_path,
        config_suffix="_api_crud_config",
        register_func=register_api_crud_routes,
        blueprint_suffix="_api_bp",
        exclusions=exclusions or [],
    )