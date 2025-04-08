import logging
from flask import Blueprint
from app.routes.base.web_utils import register_crud_routes
from app.services.crud_service import CRUDService
from app.models.setting import Setting

logger = logging.getLogger(__name__)

# Define the blueprint
settings_bp = Blueprint("settings_bp", __name__, url_prefix="/settings")

# Create a service instance
setting_service = CRUDService(Setting)

# Register all standard CRUD routes
register_crud_routes(settings_bp, "Contact", service=setting_service)
