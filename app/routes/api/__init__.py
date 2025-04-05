import logging
from flask import Blueprint

logger = logging.getLogger("flex_logger")

# Create API blueprints
companies_api_bp = Blueprint("api_companies", __name__, url_prefix="/api/companies")
contacts_api_bp = Blueprint("api_contacts", __name__, url_prefix="/api/contacts")
opportunities_api_bp = Blueprint("api_opportunities", __name__, url_prefix="/api/opportunities")
users_api_bp = Blueprint("api_users", __name__, url_prefix="/api/users")
tasks_api_bp = Blueprint("api_tasks", __name__, url_prefix="/api/tasks")
search_api_bp = Blueprint("api_search", __name__, url_prefix="/api/search")
generic_api_bp = Blueprint("api_generic", __name__, url_prefix="/api/generic")


def register_api_blueprints(app):
    """Register all API blueprints with the Flask application. Delayed import avoids circular imports."""
    logger.debug("Registering API blueprints...")

    # Delayed import to avoid circular imports
    from app.routes.api import companies, contacts, opportunities, users, tasks, search, generic

    app.register_blueprint(companies_api_bp)
    app.register_blueprint(contacts_api_bp)
    app.register_blueprint(opportunities_api_bp)
    app.register_blueprint(users_api_bp)
    app.register_blueprint(tasks_api_bp)
    app.register_blueprint(search_api_bp)
    app.register_blueprint(generic_api_bp)

    logger.debug("API blueprints registered successfully.")
