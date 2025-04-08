# import logging
# from flask import Blueprint
# from app.routes.base.components.template_renderer import render_safely
# from app.routes.base.components.entity_handler import SimpleContext
#
# logger = logging.getLogger(__name__)
#
# TABLE_NAME = 'Contact'
#
# # Define the blueprint manually for consistency with other modules
# contacts_bp = Blueprint("contacts_bp", __name__, url_prefix="/contacts")
#
#
# @contacts_bp.route("/")
# def index():
#     """Contacts list page."""
#     context = SimpleContext(title="Contacts", table_name=TABLE_NAME)
#     return render_safely("pages/tables/contacts.html", context, "Failed to load contacts.")
#
#
# @contacts_bp.route("/create")
# def create():
#     """Create contact form."""
#     context = SimpleContext(action="Create", table_name=TABLE_NAME)
#     return render_safely("pages/crud/create.html", context, "Failed to load create contact form.")
#
#
# @contacts_bp.route("/<int:item_id>")
# def view(item_id):
#     """View contact details."""
#     context = SimpleContext(action="View", table_name=TABLE_NAME)
#     return render_safely("pages/crud/view.html", context, "Failed to load contact details.")
#
#
# @contacts_bp.route("/<int:item_id>/edit")
# def edit(item_id):
#     """Edit contact form."""
#     context = SimpleContext(action="Edit", table_name=TABLE_NAME)
#     return render_safely("pages/crud/edit.html", context, "Failed to load edit contact form.")
#
#
# logger.info("Successfully set up 'Contact' routes.")