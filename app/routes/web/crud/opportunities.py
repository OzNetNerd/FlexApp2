# import logging
# from flask import Blueprint
# from app.routes.base.components.template_renderer import render_safely
# from app.routes.base.components.entity_handler import SimpleContext
#
# logger = logging.getLogger(__name__)
#
# TABLE_NAME = 'Opportunity'
#
# # Define the blueprint manually for consistency with other modules
# opportunities_bp = Blueprint("opportunities_bp", __name__, url_prefix="/opportunities")
#
#
# @opportunities_bp.route("/")
# def index():
#     """Opportunities list page."""
#     context = SimpleContext(title="Opportunities", table_name=TABLE_NAME)
#     return render_safely("pages/tables/opportunities.html", context, "Failed to load opportunities.")
#
#
# @opportunities_bp.route("/create")
# def create():
#     """Create opportunity form."""
#     context = SimpleContext(action="Create", table_name=TABLE_NAME)
#     return render_safely("pages/crud/create.html", context, "Failed to load create opportunity form.")
#
#
# @opportunities_bp.route("/<int:item_id>")
# def view(item_id):
#     """View opportunity details."""
#     context = SimpleContext(action="View", table_name=TABLE_NAME)
#     return render_safely("pages/crud/view.html", context, "Failed to load opportunity details.")
#
#
# @opportunities_bp.route("/<int:item_id>/edit")
# def edit(item_id):
#     """Edit opportunity form."""
#     context = SimpleContext(action="Edit", table_name=TABLE_NAME)
#     return render_safely("pages/crud/edit.html", context, "Failed to load edit opportunity form.")
#
#
# logger.info("Successfully set up 'Opportunity' routes.")