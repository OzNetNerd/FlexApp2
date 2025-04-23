# app/routes/web/users.py

from flask import Blueprint
from app.utils.app_logging import get_logger
from app.services.user_service import UserService
from app.models import User
from app.routes.web.route_registration import CrudRouteConfig, default_crud_templates

logger = get_logger()

users_bp = Blueprint("users_bp", __name__, url_prefix="/users")
user_service = UserService(User)
templates = default_crud_templates("User")

user_crud_config = CrudRouteConfig(
    blueprint=users_bp,
    entity_table_name="User",
    service=user_service,
    templates=templates,
)
