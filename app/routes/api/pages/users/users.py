# app/routes/api/pages/users.py

from flask import Blueprint

from app.models import User
from app.routes.api.route_registration import ApiCrudRouteConfig
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()

ENTITY_NAME = "User"
ENTITY_PLURAL_NAME = "Users"

users_api_bp = Blueprint(f"{ENTITY_PLURAL_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

user_service = CRUDService(User)

user_api_crud_config = ApiCrudRouteConfig(blueprint=users_api_bp, entity_table_name=ENTITY_NAME, service=user_service)
