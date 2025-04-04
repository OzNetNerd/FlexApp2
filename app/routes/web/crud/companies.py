import logging
from flask import Blueprint
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import Context

logger = logging.getLogger(__name__)

# Define the blueprint manually for consistency with other modules
companies_bp = Blueprint("companies", __name__, url_prefix="/companies")

@companies_bp.route("/")
def index():
    """Companies list page."""
    context = Context(title="Companies")
    return render_safely("pages/tables/companies.html", context, "Failed to load companies.")

@companies_bp.route("/create")
def create():
    """Create company form."""
    context = Context(title="Create Company")
    return render_safely("pages/crud/create.html", context, "Failed to load create company form.")

@companies_bp.route("/<int:item_id>")
def view(item_id):
    """View company details."""
    context = Context(title="View Company")
    return render_safely("pages/crud/view.html", context, "Failed to load company details.")

@companies_bp.route("/<int:item_id>/edit")
def edit(item_id):
    """Edit company form."""
    context = Context(title="Edit Company")
    return render_safely("pages/crud/edit.html", context, "Failed to load edit company form.")


logger.info("Company routes setup successfully.")
