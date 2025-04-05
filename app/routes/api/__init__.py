import logging
from flask import Blueprint
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import Context

logger = logging.getLogger(__name__)

# Create API blueprints
companies_api_bp = Blueprint('api_companies', __name__, url_prefix='/api/companies')
contacts_api_bp = Blueprint('api_contacts', __name__, url_prefix='/api/contacts')
opportunities_api_bp = Blueprint('api_opportunities', __name__, url_prefix='/api/opportunities')
users_api_bp = Blueprint('api_users', __name__, url_prefix='/api/users')
tasks_api_bp = Blueprint('api_tasks', __name__, url_prefix='/api/tasks')
search_api_bp = Blueprint('api_search', __name__, url_prefix='/api/search')
generic_api_bp = Blueprint('api_generic', __name__, url_prefix='/api/generic')


def register_api_blueprints(app):
    """Register all API blueprints with the Flask application."""
    logger.debug("Registering API blueprints...")

    app.register_blueprint(companies_api_bp)
    app.register_blueprint(contacts_api_bp)
    app.register_blueprint(opportunities_api_bp)
    app.register_blueprint(users_api_bp)
    app.register_blueprint(tasks_api_bp)
    app.register_blueprint(search_api_bp)
    app.register_blueprint(generic_api_bp)

    logger.debug("API blueprints registered successfully.")


# Import routes after blueprint definitions to avoid circular imports
from app.routes.api import companies, contacts, opportunities, users, tasks, search, generic

# API index routes — now bound to API blueprints (not web blueprints)
@contacts_api_bp.route("/")
def contacts_index():
    """API: Contacts list."""
    context = Context(title="Contacts")
    return render_safely("pages/tables/contacts.html", context, "Failed to load contacts.")

@opportunities_api_bp.route("/")
def opportunities_index():
    """API: Opportunities list."""
    context = Context(title="Opportunities")
    return render_safely("pages/tables/opportunities.html", context, "Failed to load opportunities.")

@users_api_bp.route("/")
def users_index():
    """API: Users list."""
    context = Context(title="Users")
    return render_safely("pages/tables/users.html", context, "Failed to load users.")

@tasks_api_bp.route("/")
def tasks_index():
    """API: Tasks list."""
    context = Context(title="Tasks")
    return render_safely("pages/tables/tasks.html", context, "Failed to load tasks.")
