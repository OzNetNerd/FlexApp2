# app/routes/web_router.py

from flask import Flask
from app.utils.router_utils import register_application_blueprints
from app.utils.app_logging import get_logger

logger = get_logger()


def register_web_blueprints(app: Flask) -> None:
    """Auto-discover and register all web blueprints with the Flask application."""
    logger.info("Registering web blueprints")

    register_application_blueprints(
        app=app,
        package_path="app.routes.web.pages",
        blueprint_suffix="_bp",
        exclusions=["components"]
    )