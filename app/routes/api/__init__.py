from flask import Blueprint
import logging

logger = logging.getLogger(__name__)

# Create blueprint objects for API endpoints
api_users_bp = Blueprint("api_users", __name__, url_prefix="/api/users")
api_companies_bp = Blueprint("api_companies", __name__, url_prefix="/api/companies")
api_contacts_bp = Blueprint("api_contacts", __name__, url_prefix="/api/contacts")
api_opportunities_bp = Blueprint("api_opportunities", __name__, url_prefix="/api/opportunities")
api_table_config_bp = Blueprint("api_table_config", __name__, url_prefix="/api/table-config")
api_tasks_bp = Blueprint("api_tasks", __name__, url_prefix="/api/tasks")  # ✅ Added

# Import blueprint route handlers (ensures routes are registered)
from app.routes.api.table_config import api_table_config_bp
from app.routes.api.opportunities import api_opportunities_bp
from app.routes.api.contacts import api_contacts_bp
from app.routes.api.companies import api_companies_bp
from app.routes.api.users import api_users_bp
from app.routes.api.tasks import api_tasks_bp  # ✅ Added

def register_api_blueprints(app):
    """Attach all API blueprints to the Flask app instance.

    This allows the app to serve RESTful API routes for
    users, companies, contacts, opportunities, table config, and tasks.

    Args:
        app (Flask): The Flask app instance to register routes on.

    Returns:
        None
    """
    logger.debug("Registering API blueprints...")

    app.register_blueprint(api_users_bp)
    app.register_blueprint(api_companies_bp)
    app.register_blueprint(api_contacts_bp)
    app.register_blueprint(api_opportunities_bp)
    app.register_blueprint(api_table_config_bp)
    app.register_blueprint(api_tasks_bp)  # ✅ Registered

    logger.debug("API blueprints registered successfully.")
