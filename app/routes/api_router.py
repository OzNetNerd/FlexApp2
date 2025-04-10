# web_router.py

import logging
from flask import Flask, Blueprint

from app.routes.api.companies import companies_api_bp
from app.routes.api.contacts import contacts_api_bp
from app.routes.api.opportunities import opportunities_api_bp
from app.routes.api.search import search_bp
from app.routes.api.tasks import tasks_api_bp
from app.routes.api.users import users_api_bp

# from app.routes.web.settings import settings_bp
# from app.routes.web.auth import auth_bp
# from app.routes.web.home import home_bp


logger = logging.getLogger(__name__)


# Define blueprints with original names for template compatibility
# relationships_bp = Blueprint("relationships", __name__, url_prefix="/relationships")
# crisp_scores_bp = Blueprint("crisp_scores", __name__, url_prefix="/crisp_scores")
# relationships_bp,
# crisp_scores_bp


# List of blueprints to register
BLUEPRINTS = [
    companies_api_bp,
    contacts_api_bp,
    opportunities_api_bp,
    search_bp,
    tasks_api_bp,
    users_api_bp,
]


def register_web_blueprints(app: Flask) -> None:
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