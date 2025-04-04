# app/routes/web/__init__.py

import logging
from flask import Blueprint
from app.routes.web.auth import login, logout
from app.routes.web.index import index_bp
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import Context

logger = logging.getLogger(__name__)

# Create blueprints for web UI
users_bp = Blueprint("users", __name__, url_prefix="/users")
companies_bp = Blueprint("companies", __name__, url_prefix="/companies")
contacts_bp = Blueprint("contacts", __name__, url_prefix="/contacts")
opportunities_bp = Blueprint("opportunities", __name__, url_prefix="/opportunities")
relationships_bp = Blueprint("relationships", __name__, url_prefix="/relationships")
crisp_scores_bp = Blueprint("crisp_scores_bp", __name__, url_prefix="/crisp-scores")
auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

# Register login/logout routes with auth blueprint
auth_bp.add_url_rule("/login", view_func=login, methods=["GET", "POST"])
auth_bp.add_url_rule("/logout", view_func=logout, methods=["GET"])

# Add index routes for each blueprint - USE FUNCTION NAME "index" NOT "companies_index"
@companies_bp.route("/")
def index():
    """Companies list page."""
    context = Context(title="Companies")
    return render_safely("pages/tables/companies.html", context, "Failed to load companies.")

@contacts_bp.route("/")
def index():
    """Contacts list page."""
    context = Context(title="Contacts")
    return render_safely("pages/tables/contacts.html", context, "Failed to load contacts.")

@opportunities_bp.route("/")
def index():
    """Opportunities list page."""
    context = Context(title="Opportunities")
    return render_safely("pages/tables/opportunities.html", context, "Failed to load opportunities.")

@users_bp.route("/")
def index():
    """Users list page."""
    context = Context(title="Users")
    return render_safely("pages/tables/users.html", context, "Failed to load users.")

@tasks_bp.route("/")
def index():
    """Tasks list page."""
    context = Context(title="Tasks")
    return render_safely("pages/tables/tasks.html", context, "Failed to load tasks.")

@settings_bp.route("/")
def index():
    """Settings page."""
    context = Context(title="Settings")
    return render_safely("pages/misc/settings.html", context, "Failed to load settings.")


@relationships_bp.route("/")
def index():
    """Relationships list page."""
    context = Context(title="Relationships")
    return render_safely("pages/tables/relationships.html", context, "Failed to load relationships.")

# Add these routes for each blueprint
@users_bp.route('/create')
def create():
    context = Context(title="Create User")
    return render_safely("pages/crud/create.html", context, "Failed to load create user form.")

@users_bp.route('/<int:item_id>')
def view(item_id):
    context = Context(title="View User")
    return render_safely("pages/crud/view.html", context, "Failed to load user details.")

@users_bp.route('/<int:item_id>/edit')
def edit(item_id):
    context = Context(title="Edit User")
    return render_safely("pages/crud/edit.html", context, "Failed to load edit user form.")

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