from flask import Blueprint
import logging

logger = logging.getLogger(__name__)

# Create blueprints for web UI
main_bp = Blueprint('main', __name__)
users_bp = Blueprint('users', __name__, url_prefix='/users')
companies_bp = Blueprint('companies', __name__, url_prefix='/companies')
contacts_bp = Blueprint('contacts', __name__, url_prefix='/contacts')
opportunities_bp = Blueprint('opportunities', __name__, url_prefix='/opportunities')

# Import route definitions to register with blueprints
from routes.web.main import main_bp
from routes.web.users import users_bp
from routes.web.companies import companies_bp
from routes.web.contacts import contacts_bp
from routes.web.opportunities import opportunities_bp


def register_web_blueprints(app):
    """Register all web blueprints with the Flask application."""
    logger.debug("Registering web blueprints...")

    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(opportunities_bp)

    logger.debug("Web blueprints registered successfully.")