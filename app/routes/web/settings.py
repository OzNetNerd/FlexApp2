import logging
from flask import Blueprint
from app.routes.web.components.web_utils import register_route, CrudRouteConfig, SimpleContext
from app.services.crud_service import CRUDService
from app.models.setting import Setting

logger = logging.getLogger(__name__)

# Define the blueprint
settings_bp = Blueprint("settings_bp", __name__, url_prefix="/settings")

# Create a service instance
setting_service = CRUDService(Setting)

# Register all standard CRUD routes
setting_crud_config = CrudRouteConfig(blueprint=settings_bp, entity_table_name="Setting", service=setting_service)

register_route(
    blueprint=settings_bp,
    url="/",
    template_path="pages/settings.html",
    title="Settings",
    context_provider=SimpleContext,
    endpoint="index",
)