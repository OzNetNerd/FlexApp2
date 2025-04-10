import logging
from flask import Blueprint
from app.routes.web.components.web_utils import register_crud_routes, CrudRouteConfig
from app.services.crud_service import CRUDService
from app.models.user import User

logger = logging.getLogger(__name__)

# Define the blueprint
users_bp = Blueprint("users_bp", __name__, url_prefix="/users")

# Create a service instance
user_service = CRUDService(User)

# Register all standard CRUD routes
user_crud_config = CrudRouteConfig(blueprint=users_bp, entity_table_name="User", service=user_service)
register_crud_routes(user_crud_config)
