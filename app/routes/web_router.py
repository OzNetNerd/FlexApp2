# app/routes/web_router.py

from flask import Flask

from app.routes.web.route_registration import register_crud_routes
from app.utils.router_utils import register_blueprint_routes


def register_web_blueprints(app: Flask) -> None:
    """Auto-wire CRUD routes and register all web blueprints."""
    register_blueprint_routes(
        app=app,
        package_path="app.routes.web",
        config_suffix="_crud_config",
        register_func=register_crud_routes,
        blueprint_suffix="_bp",
        exclusions=["components"]
    )