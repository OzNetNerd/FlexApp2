import logging
from flask import Blueprint
from app.routes.base.web_utils import register_crud_routes
from app.services.crud_service import CRUDService
from app.models.setting import Setting
from app.routes.base.web_utils import CrudRouteConfig


logger = logging.getLogger(__name__)

# Define the blueprint
settings_bp = Blueprint("settings_bp", __name__, url_prefix="/settings")

# Create a service instance
setting_service = CRUDService(Setting)

# Register all standard CRUD routes
setting_crud_config = CrudRouteConfig(
    blueprint=settings_bp,
    entity_name="Setting",
    service=setting_service
)
register_crud_routes(setting_crud_config)
