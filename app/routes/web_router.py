# web_router.py

from flask import Flask, Blueprint

from app.routes.web.companies import companies_bp
from app.routes.web.contacts import contacts_bp
from app.routes.web.opportunities import opportunities_bp
from app.routes.web.users import users_bp
from app.routes.web.tasks import tasks_bp
from app.routes.web.settings import settings_bp
from app.routes.web.auth import auth_bp
from app.routes.web.home import home_bp
from app.routes.web.srs import srs_bp

# Register the blueprint with your Flask app
from app.utils.app_logging import get_logger
logger = get_logger()


# Define blueprints with original names for template compatibility
relationships_bp = Blueprint("relationships", __name__, url_prefix="/relationships")
crisp_scores_bp = Blueprint("crisp_scores", __name__, url_prefix="/crisp_scores")

# List of blueprints to register
BLUEPRINTS = [
    companies_bp,
    contacts_bp,
    opportunities_bp,
    users_bp,
    tasks_bp,
    settings_bp,
    auth_bp,
    home_bp,
    relationships_bp,
    crisp_scores_bp,
    srs_bp,
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
