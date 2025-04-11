# api/contacts.py

import logging
from flask import Blueprint
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig
from app.models import Contact
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)

ENTITY_NAME = "Contact"
ENTITY_PLURAL_NAME = "Contacts"

contacts_api_bp = Blueprint(f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")
contact_service = CRUDService(Contact)

# Register all standard CRUD API routes
contact_api_crud_config = ApiCrudRouteConfig(
    blueprint=contacts_api_bp,
    entity_table_name=ENTITY_NAME,
    service=contact_service
)
register_api_crud_routes(contact_api_crud_config)

logger.info(f"{ENTITY_PLURAL_NAME} API routes registered successfully.")
