import logging
from flask import Blueprint
from app.routes.base.web_utils import register_page_route
from app.services.crud_service import CRUDService
from app.models.setting import Setting

logger = logging.getLogger(__name__)

# Define the blueprint
settings_bp = Blueprint("settings_bp", __name__, url_prefix="/settings")

# Create a service instance
settings_service = CRUDService(Setting)

# Register the main settings page route
register_page_route(
    blueprint=settings_bp,
    url="/",
    template_path="settings/list.html",
    context_provider=lambda: {"items": settings_service.get_all()},
    endpoint="settings_list"
)
