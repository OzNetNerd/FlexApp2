# app/routes/web_router.py

from flask import Flask

from app.routes.web.utils.route_registration import register_crud_routes
from app.utils.router_utils import register_blueprint_routes, recursive_discover_routes
from app.utils.app_logging import get_logger

logger = get_logger()


def register_web_blueprints(app: Flask) -> None:
    """Auto-discover and register all web blueprints with the Flask application.

    This function uses a convention-based approach to automatically find and register
    Flask blueprints throughout the application:

    1. It recursively scans all Python modules in the 'app.routes.web' package
    2. For each module, it looks for module-level variables ending with '_bp'
       (e.g., 'contacts_bp', 'users_bp', etc.)
    3. When found, these blueprints are automatically registered with the Flask app
    4. It also automatically imports and registers all route modules in blueprint packages

    Args:
        app: The Flask application instance where blueprints will be registered

    Note:
        Modules in the 'components' directory are excluded from auto-registration.
    """
    logger.info("Auto-discovering web blueprints")

    # Register all blueprints first
    blueprints = register_blueprint_routes(
        app=app,
        package_path="app.routes.web.pages",
        config_suffix="_crud_config",
        register_func=register_crud_routes,
        blueprint_suffix="_bp",
        exclusions=["components"],
        return_blueprints=True
    )

    logger.info(f"Discovered {len(blueprints)} blueprints")

    # Then auto-discover all routes in the web.pages package
    logger.info("Auto-discovering route modules")
    recursive_discover_routes("app.routes.web.pages")

    logger.info("Web blueprints and routes registered successfully")