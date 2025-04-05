import logging
from flask import Blueprint, abort, render_template
from flask_login import current_user

from app.models.user import User
from app.routes.web.crud.components.generic_crud_routes import GenericWebRoutes
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import SimpleContext

logger = logging.getLogger(__name__)

# Define the blueprint
users_bp = Blueprint("users", __name__, url_prefix="/users")


class UsersCRUDRoutes(GenericWebRoutes):
    """
    Custom CRUD routes for User model.
    """

    def _preprocess_form_data(self, form_data):
        return form_data

    def index(self):
        """Overrides the default index for Users."""
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)

        return render_template(
            self.index_template,
            title="Users",
        )


# Register the CRUD route handler
users_routes = UsersCRUDRoutes(
    blueprint=users_bp,
    model=User,
    index_template="pages/tables/users.html",
    required_fields=[],
    unique_fields=[],
)


# Optional: Custom route (not part of CRUD)
@users_bp.route("/dashboard")
def dashboard():
    """User dashboard with additional statistics and information."""
    context = SimpleContext(title="User Dashboard")
    return render_safely("pages/users/dashboard.html", context, "Failed to load user dashboard.")


# Optional: Custom validator
def validate_user_data(form_data):
    """Validate user form data and return any errors."""
    errors = []

    for field in ["username", "name", "email"]:
        if not form_data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required.")

    if form_data.get("username"):
        existing = User.query.filter_by(username=form_data["username"]).first()
        if existing and (not form_data.get("id") or existing.id != int(form_data["id"])):
            errors.append(f"Username '{form_data['username']}' is already in use.")

    return errors


logger.info("User routes setup successfully.")
