import logging
from app.models import User
from app.routes.blueprint_factory import create_blueprint
from app.routes.base.crud_factory import register_crud_routes
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import Context

logger = logging.getLogger(__name__)

# Create blueprint
users_bp = create_blueprint("users")

# Register standard CRUD routes
register_crud_routes(users_bp, "user")


# Add custom route handlers if needed
@users_bp.route('/dashboard')
def dashboard():
    """User dashboard with additional statistics and information."""
    context = Context(title="User Dashboard")
    return render_safely("pages/users/dashboard.html", context, "Failed to load user dashboard.")


# Helper function to validate user data
def validate_user_data(form_data):
    """Validate user form data and return any errors."""
    errors = []

    # Check required fields
    for field in ["username", "name", "email"]:
        if not form_data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required.")

    # Check uniqueness of username
    if form_data.get("username"):
        existing = User.query.filter_by(username=form_data["username"]).first()
        if existing and (not form_data.get("id") or existing.id != int(form_data["id"])):
            errors.append(f"Username '{form_data['username']}' is already in use.")

    return errors


logger.info("User routes setup successfully.")