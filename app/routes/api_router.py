# api_router.py
from flask import Flask

from app.routes.api.companies import companies_api_bp
from app.routes.api.contacts import contacts_api_bp
from app.routes.api.opportunities import opportunities_api_bp
from app.routes.api.search import search_bp
from app.routes.api.tasks import tasks_api_bp
from app.routes.api.users import users_api_bp
from app.routes.api.notes import notes_api_bp
from app.routes.api.srs import srs_api_bp

from app.utils.app_logging import get_logger
logger = get_logger()

# List of blueprints to register
BLUEPRINTS = [
    companies_api_bp,
    contacts_api_bp,
    opportunities_api_bp,
    search_bp,
    tasks_api_bp,
    users_api_bp,
    notes_api_bp,
    srs_api_bp,
]


def register_api_blueprints(app: Flask) -> None:
    """
    Central function for registering all blueprints in the application.

    This function serves as the single point of registration for all blueprints
    in the application. Each blueprint represents a distinct functional area or
    feature set within the application. Adding new blueprints to this function
    will make them available throughout the application.

    Args:
        app (Flask): The Flask application instance to which blueprints will be registered

    Returns:
        None: This function modifies the app in-place and does not return a value

    Example:
        register_web_blueprints(app)
    """
    logger.info("Registering all web blueprints...")

    # Loop through blueprints and register each one
    for bp in BLUEPRINTS:
        app.register_blueprint(bp)
        logger.info(f"Blueprint '{bp.name}' registered successfully")
