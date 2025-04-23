from flask import Blueprint
from app.utils.app_logging import get_logger
from app.services.user_service import UserService
from app.models import User
from app.routes.api.route_registration import ApiCrudRouteConfig

logger = get_logger()

ENTITY_NAME = "User"
ENTITY_PLURAL_NAME = "Users"

users_api_bp = Blueprint(f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

user_service = UserService(User)

user_api_crud_config = ApiCrudRouteConfig(blueprint=users_api_bp, entity_table_name=ENTITY_NAME, service=user_service)
