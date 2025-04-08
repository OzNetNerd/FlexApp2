# web_router.py

import logging
from flask import Flask, Blueprint

from app.routes.web.companies import companies_bp
from app.routes.web.contacts import contacts_bp
from app.routes.web.opportunities import opportunities_bp
from app.routes.web.users import users_bp
from app.routes.web.tasks import tasks_bp
from app.routes.web.settings import settings_bp
from app.routes.web.auth import auth_bp
from app.routes.web.home import home_bp

# Register the blueprint with your Flask app


logger = logging.getLogger(__name__)


# Define blueprints with original names for template compatibility
relationships_bp = Blueprint('relationships', __name__, url_prefix='/relationships')
crisp_scores_bp = Blueprint('crisp_scores', __name__, url_prefix='/crisp_scores')

def register_application_blueprints(app: Flask) -> None:
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
        register_application_blueprints(app)
    """
    logger.info("Registering all application blueprints...")

    app.register_blueprint(companies_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)