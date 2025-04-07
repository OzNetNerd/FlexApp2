import logging
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import SimpleContext
from flask import Blueprint, request, url_for, redirect, flash



logger = logging.getLogger(__name__)

TABLE_NAME = 'Company'

# Define the blueprint manually for consistency with other modules
companies_bp = Blueprint("companies", __name__, url_prefix="/companies")


@companies_bp.route("/")
def index():
    """Companies list page."""
    context = SimpleContext(title="Companies", table_name=TABLE_NAME)
    return render_safely("pages/tables/companies.html", context, "Failed to load companies.")


@companies_bp.route("/create")
def create():
    """Create company form."""
    context = SimpleContext(action="Create", table_name=TABLE_NAME)
    return render_safely("pages/crud/create.html", context, "Failed to load create company form.")


import requests

@companies_bp.route("/<int:item_id>")
def view(item_id):
    """View company details via API call."""
    resp = requests.get(url_for('companies_api.get_one', item_id=item_id, _external=True))
    if resp.status_code != 200:
        flash("Company not found.", "danger")
        return redirect(url_for("companies.list"))

    context = SimpleContext(
        action="View",
        table_name=TABLE_NAME,
        item=resp.json()
    )
    return render_safely("pages/crud/view.html", context, "Failed to load company details.")



@companies_bp.route("/<int:item_id>/edit")
def edit(item_id):
    """Edit company form."""
    context = SimpleContext(action="Edit", table_name=TABLE_NAME)
    return render_safely("pages/crud/edit.html", context, "Failed to load edit company form.")


logger.info("Successfully set up 'Company' routes.")
