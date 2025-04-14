import logging
from flask import Blueprint
from app.routes.web.route_registration import register_crud_routes, CrudRouteConfig, CrudTemplates
from app.services.crud_service import CRUDService
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)

# Define the blueprint
opportunities_bp = Blueprint("opportunities_bp", __name__, url_prefix="/opportunities")

# Create a service instance
opportunity_service = CRUDService(Opportunity)

# Define custom templates for opportunities
custom_templates = CrudTemplates(
    view="pages/crud/create_view_edit_opportunity.html",
    edit="pages/crud/create_view_edit_opportunity.html",

)

# Add debug logging to verify the templates are set correctly
logger.info(f"Custom templates: {custom_templates.to_dict()}")

# Register all standard CRUD routes with custom templates
opportunity_crud_config = CrudRouteConfig(
    blueprint=opportunities_bp,
    entity_table_name="Opportunity",
    service=opportunity_service,
    templates=custom_templates
)
register_crud_routes(opportunity_crud_config)
