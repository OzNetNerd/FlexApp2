import logging
from flask import Blueprint
from app.routes.base.web_utils import register_blueprint_routes
from app.services.crud_service import CRUDService
from app.models.user import User

logger = logging.getLogger(__name__)

# Define the blueprint
users_bp = Blueprint("users", __name__, url_prefix="/users")

# Create a service instance
user_service = CRUDService(User)

# Register all standard CRUD routes
register_blueprint_routes(users_bp, "User", service=user_service)
