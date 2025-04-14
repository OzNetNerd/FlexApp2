# web/users.py

import logging
from flask import Blueprint
from app.routes.web.route_registration import register_crud_routes, CrudRouteConfig, CrudTemplates
from app.services.crud_service import CRUDService
from app.models.user import User

logger = logging.getLogger(__name__)

# Define the blueprint
users_bp = Blueprint("users_bp", __name__, url_prefix="/users")

# Create a service instance
user_service = CRUDService(User)

# Define custom templates for users
custom_templates = CrudTemplates(
    create="pages/crud/create_view_edit_user.html",
    view="pages/crud/create_view_edit_user.html",
    edit="pages/crud/create_view_edit_user.html",
)

# Log the custom templates for debugging
logger.info(f"Custom templates: {custom_templates.to_dict()}")

# Register all standard CRUD routes with custom templates
user_crud_config = CrudRouteConfig(blueprint=users_bp, entity_table_name="User", service=user_service, templates=custom_templates)
register_crud_routes(user_crud_config)
