# src/interfaces/web/router.py

from typing import Callable, List, Optional

from flask import Flask

from src.interfaces.web.route_registration import register_crud_routes
from src.infrastructure.utils.router_utils import register_blueprint_routes


def register_web_blueprints(
        app: Flask,
        package_path: str = "src.interfaces.web.pages",
        exclusions: Optional[List[str]] = None
) -> None:
    """Register web blueprints with their CRUD routes automatically.

    This function uses a convention-based approach to find and register Flask blueprints:
    1. Scans all Python modules in the specified package
    2. Looks for module-level variables ending with '_bp'
    3. Registers found blueprints with the Flask app

    Args:
        app: The Flask application instance
        package_path: The package path to scan for blueprint modules
        exclusions: Optional list of module names to exclude from registration

    Returns:
        None

    Note:
        To create a discoverable blueprint module:
        - Define a module-level variable ending with '_bp'
        - Example: contact_bp = create_crud_blueprint(BlueprintConfig(model_class=Contact))
    """
    register_blueprint_routes(
        app=app,
        package_path=package_path,
        config_suffix="_crud_config",
        register_func=register_crud_routes,
        blueprint_suffix="_bp",
        exclusions=exclusions or ["components"],
    )