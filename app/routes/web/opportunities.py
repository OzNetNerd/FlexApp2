import logging
from flask import Blueprint
from app.routes.base.web_utils import register_crud_routes
from app.services.crud_service import CRUDService
from app.models.opportunity import Opportunity
from app.routes.base.web_utils import CrudRouteConfig

logger = logging.getLogger(__name__)

# Define the blueprint
opportunities_bp = Blueprint("opportunities_bp", __name__, url_prefix="/opportunities")

# Create a service instance
opportunity_service = CRUDService(Opportunity)

# Register all standard CRUD routes
opportunity_crud_config = CrudRouteConfig(blueprint=opportunities_bp, entity_table_name="Opportunity", service=opportunity_service)
register_crud_routes(opportunity_crud_config)
