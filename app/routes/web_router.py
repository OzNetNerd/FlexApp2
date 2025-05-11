# app/routes/web_router.py

from flask import Flask
from app.utils.router_utils import discover_blueprint_packages
from app.utils.app_logging import get_logger
import pkgutil
import importlib

logger = get_logger()


# app/routes/web_router.py - updated register_web_blueprints function

def register_web_blueprints(app: Flask) -> None:
    """Auto-discover and register all web blueprints with the Flask application."""
    logger.info("Auto-discovering web blueprints")

    # First discover all blueprints and their packages
    blueprints = discover_blueprint_packages(
        package_path="app.routes.web.pages",
        exclusions=["components"]
    )

    logger.info(f"Discovered {len(blueprints)} blueprints")

    # Import all route modules before registering blueprints
    for bp_name, (_, package_path) in blueprints.items():
        if package_path:
            # Import all modules in the blueprint's package to register routes
            for _, route_module_name, _ in pkgutil.iter_modules(
                    importlib.import_module(package_path).__path__,
                    package_path + '.'
            ):
                try:
                    logger.debug(f"Importing route module: {route_module_name}")
                    importlib.import_module(route_module_name)
                except ImportError as e:
                    logger.error(f"Error importing route module {route_module_name}: {e}")

    # Now register the blueprints after their routes are defined
    for bp_name, (blueprint, _) in blueprints.items():
        logger.debug(f"Registering blueprint: {blueprint.name} @ {blueprint.url_prefix}")
        app.register_blueprint(blueprint)

    logger.info("Web blueprints and routes registered successfully")