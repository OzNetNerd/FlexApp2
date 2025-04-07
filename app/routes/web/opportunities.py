import logging
from flask import Blueprint
from app.routes.base.web_utils import register_blueprint_routes
from app.services.crud_service import CRUDService
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)

# Define the blueprint
opportunities_bp = Blueprint("opportunities", __name__, url_prefix="/opportunities")

# Create a service instance
opportunity_service = CRUDService(Opportunity)

# Register all standard CRUD routes
register_blueprint_routes(opportunities_bp, "Opportunity", service=opportunity_service)
