import logging
from flask import Blueprint
from app.routes.base.web_utils import register_blueprint_routes
from app.services.crud_service import CRUDService
from app.models.setting import Setting

logger = logging.getLogger(__name__)

# Define the blueprint
settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

# Create a service instance
settings_service = CRUDService(Setting)

# Register all standard CRUD routes
register_blueprint_routes(settings_bp, "Setting", service=settings_service)
