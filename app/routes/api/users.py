# api/users.py

import logging
from flask import Blueprint
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig
from app.models import User
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

ENTITY_NAME = "User"
ENTITY_PLURAL_NAME = "Users"

users_api_bp = Blueprint(f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")
user_service = UserService(User)

# Register all standard CRUD API routes
user_api_crud_config = ApiCrudRouteConfig(blueprint=users_api_bp, entity_table_name=ENTITY_NAME, service=user_service)
register_api_crud_routes(user_api_crud_config)

logger.info(f"{ENTITY_PLURAL_NAME} API routes registered successfully.")
