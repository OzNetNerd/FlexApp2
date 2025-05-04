# app/routes/web_router.py

from flask import Flask

from app.routes.web.utils.route_registration import register_crud_routes
from app.utils.router_utils import register_blueprint_routes


def register_web_blueprints(app: Flask) -> None:
    """Auto-discover and register all web blueprints with the Flask application.

    This function uses a convention-based approach to automatically find and register
    Flask blueprints throughout the application:

    1. It recursively scans all Python modules in the 'app.routes.web' package
    2. For each module, it looks for module-level variables ending with '_bp'
       (e.g., 'contacts_bp', 'users_bp', etc.)
    3. When found, these blueprints are automatically registered with the Flask app

    To create a discoverable blueprint module:
    - Define a module-level variable ending with '_bp' that contains a Flask Blueprint
    - Example: contact_bp = create_crud_blueprint(BlueprintConfig(model_class=Contact))

    Args:
        app: The Flask application instance where blueprints will be registered

    Note:
        Modules in the 'components' directory are excluded from auto-registration.
    """
    register_blueprint_routes(
        app=app,
        package_path="app.routes.web.pages",
        config_suffix="_crud_config",
        register_func=register_crud_routes,
        blueprint_suffix="_bp",
        exclusions=["components"],
    )
