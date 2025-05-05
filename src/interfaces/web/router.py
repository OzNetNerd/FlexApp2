# src/interfaces/web/router.py

from typing import Callable, List, Optional

from flask import Flask


from src.interfaces.web.routes.crud_routes import register_crud_routes
from src.infrastructure.utils.router_utils import register_blueprint_routes


def register_web_blueprints(app: Flask, package_path: str = "src.interfaces.web.pages", exclusions: Optional[List[str]] = None) -> None:
    """Register web blueprints with their CRUD routes automatically.

    Args:
        app: The Flask application instance
        package_path: The package path to scan for blueprint modules
        exclusions: Optional list of module names to exclude from registration
    """
    register_blueprint_routes(
        app=app,
        package_path=package_path,
        config_suffix="_crud_config",
        register_func=register_crud_routes,
        blueprint_suffix="_bp",
        exclusions=exclusions or ["components"],
    )
