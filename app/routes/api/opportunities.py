# api/opportunities.py

import logging
from app.routes.blueprint_factory import create_blueprint
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig
from app.models import Opportunity
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)

# Create API blueprint with /api prefix for opportunities
opportunities_api_bp = create_blueprint("api_opportunities", url_prefix="/api/opportunities")
opportunity_service = CRUDService(Opportunity)

# Register all standard CRUD API routes
opportunity_api_crud_config = ApiCrudRouteConfig(
    blueprint=opportunities_api_bp,
    entity_table_name="Opportunity",
    service=opportunity_service
)
register_api_crud_routes(opportunity_api_crud_config)

logger.info("Opportunities API routes registered successfully.")