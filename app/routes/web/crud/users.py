# import logging
# from flask import Blueprint
# from app.routes.base.components.template_renderer import render_safely
# from app.routes.base.components.entity_handler import SimpleContext
#
# logger = logging.getLogger(__name__)
#
# TABLE_NAME = 'User'
#
# # Define the blueprint manually for consistency with other modules
# users_bp = Blueprint("users", __name__, url_prefix="/users")
#
#
# @users_bp.route("/")
# def index():
#     """Users list page."""
#     context = SimpleContext(title="Users", table_name=TABLE_NAME)
#     return render_safely("pages/tables/users.html", context, "Failed to load users.")
#
#
# @users_bp.route("/create")
# def create():
#     """Create user form."""
#     context = SimpleContext(action="Create", table_name=TABLE_NAME)
#     return render_safely("pages/crud/create.html", context, "Failed to load create user form.")
#
#
# @users_bp.route("/<int:item_id>")
# def view(item_id):
#     """View user details."""
#     context = SimpleContext(action="View", table_name=TABLE_NAME)
#     return render_safely("pages/crud/view.html", context, "Failed to load user details.")
#
#
# @users_bp.route("/<int:item_id>/edit")
# def edit(item_id):
#     """Edit user form."""
#     context = SimpleContext(action="Edit", table_name=TABLE_NAME)
#     return render_safely("pages/crud/edit.html", context, "Failed to load edit user form.")
#
#
# @users_bp.route("/dashboard")
# def dashboard():
#     """User dashboard with additional statistics and information."""
#     context = SimpleContext(title="User Dashboard", table_name=TABLE_NAME)
#     return render_safely("pages/users/dashboard.html", context, "Failed to load user dashboard.")
#
#
# logger.info("Successfully set up 'User' routes.")