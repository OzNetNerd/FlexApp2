from flask import Blueprint
import logging
from flask_login import LoginManager
from routes.web.auth import login
from routes.web.auth import logout
from routes.web.auth import load_user


logger = logging.getLogger(__name__)

# Create blueprints for web UI
main_bp = Blueprint('main', __name__)
users_bp = Blueprint('users', __name__, url_prefix='/users')
companies_bp = Blueprint('companies', __name__, url_prefix='/companies')
contacts_bp = Blueprint('contacts', __name__, url_prefix='/contacts')
opportunities_bp = Blueprint('opportunities', __name__, url_prefix='/opportunities')
relationships_bp = Blueprint('relationships_bp', __name__, url_prefix='/relationships')
crisp_scores_bp = Blueprint('crisp_scores_bp', __name__, url_prefix='/crisp-scores')
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')
auth_bp.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
auth_bp.add_url_rule('/logout', view_func=logout, methods=['GET'])

login_manager = LoginManager()
login_manager.user_loader(load_user)


# Import route definitions to register with blueprints
from routes.web.main import main_bp
from routes.web.users import users_bp
from routes.web.companies import companies_bp
from routes.web.contacts import contacts_bp
from routes.web.opportunities import opportunities_bp
from routes.web.relationship import relationships_bp
from routes.web.crisp_score import crisp_scores_bp
from routes.web.auth import load_user

def register_web_blueprints(app):
    """Register all web blueprints with the Flask application."""
    logger.debug("Registering web blueprints...")

    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(relationships_bp)
    app.register_blueprint(crisp_scores_bp)
    app.register_blueprint(auth_bp)

    logger.debug("Web blueprints registered successfully.")
