import logging
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import Context
from app.routes.blueprint_factory import create_blueprint

logger = logging.getLogger(__name__)

# Create blueprint
companies_bp = create_blueprint("companies")

# Don't use register_crud_routes AND define the routes manually
# Just define them manually

@companies_bp.route("/")
def index():
    """Companies list page."""
    context = Context(title="Companies")
    return render_safely("pages/tables/companies.html", context, "Failed to load companies.")

@companies_bp.route('/create')
def create():
    context = Context(title="Create Company")
    return render_safely("pages/crud/create.html", context, "Failed to load create company form.")

@companies_bp.route('/<int:item_id>')
def view(item_id):
    context = Context(title="View Company")
    return render_safely("pages/crud/view.html", context, "Failed to load company details.")

@companies_bp.route('/<int:item_id>/edit')
def edit(item_id):
    context = Context(title="Edit Company")
    return render_safely("pages/crud/edit.html", context, "Failed to load edit company form.")