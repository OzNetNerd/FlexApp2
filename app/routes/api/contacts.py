# api/contacts.py

import logging
from app.routes.blueprint_factory import create_blueprint
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig
from app.models import Contact
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)

# Create API blueprint with /api prefix for contacts
contacts_api_bp = create_blueprint("api_contacts", url_prefix="/api/contacts")
contact_service = CRUDService(Contact)

# Register all standard CRUD API routes
contact_api_crud_config = ApiCrudRouteConfig(
    blueprint=contacts_api_bp,
    entity_table_name="Contact",
    service=contact_service
)
register_api_crud_routes(contact_api_crud_config)

logger.info("Contact API routes registered successfully.")