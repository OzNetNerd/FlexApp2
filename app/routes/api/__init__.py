import logging
from app.routes.web.auth import login, logout, auth_bp
from app.routes.web.index import index_bp
from app.routes.web.crud.companies import companies_bp
from flask import Blueprint

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

    # Register API blueprints
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

# Add index routes for each blueprint - these should eventually be moved to their own modules
@contacts_bp.route("/")
def contacts_index():
    """Contacts list page."""
    from app.routes.base.components.template_renderer import render_safely
    from app.routes.base.components.entity_handler import Context
    context = Context(title="Contacts")
    return render_safely("pages/tables/contacts.html", context, "Failed to load contacts.")

@opportunities_bp.route("/")
def opportunities_index():
    """Opportunities list page."""
    from app.routes.base.components.template_renderer import render_safely
    from app.routes.base.components.entity_handler import Context
    context = Context(title="Opportunities")
    return render_safely("pages/tables/opportunities.html", context, "Failed to load opportunities.")

@users_bp.route("/")
def users_index():
    """Users list page."""
    from app.routes.base.components.template_renderer import render_safely
    from app.routes.base.components.entity_handler import Context
    context = Context(title="Users")
    return render_safely("pages/tables/users.html", context, "Failed to load users.")

@tasks_bp.route("/")
def tasks_index():
    """Tasks list page."""
    from app.routes.base.components.template_renderer import render_safely
    from app.routes.base.components.entity_handler import Context
    context = Context(title="Tasks")
    return render_safely("pages/tables/tasks.html", context, "Failed to load tasks.")

@settings_bp.route("/")
def settings_index():
    """Settings page."""
    from app.routes.base.components.template_renderer import render_safely
    from app.routes.base.components.entity_handler import Context
    context = Context(title="Settings")
    return render_safely("pages/misc/settings.html", context, "Failed to load settings.")

@relationships_bp.route("/")
def relationships_index():
    """Relationships list page."""
    from app.routes.base.components.template_renderer import render_safely
    from app.routes.base.components.entity_handler import Context
    context = Context(title="Relationships")
    return render_safely("pages/tables/relationships.html", context, "Failed to load relationships.")

def register_web_blueprints(app):
    """Register all web blueprints with the Flask application."""
    logger.debug("Registering web blueprints...")

    app.register_blueprint(index_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(relationships_bp)
    app.register_blueprint(crisp_scores_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(settings_bp)

    logger.debug("Web blueprints registered successfully.")