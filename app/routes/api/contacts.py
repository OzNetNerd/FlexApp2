from models import Contact
from routes.api import api_contacts_bp
from routes.api.generic import GenericAPIRoutes
from services.crud_service import CRUDService
import logging

logger = logging.getLogger(__name__)

# API routes
contact_service = CRUDService()
logger.debug("Instantiating GenericAPIRoutes for the Contact model.")
contact_api_routes = GenericAPIRoutes(
    blueprint=api_contacts_bp,
    model=Contact,
    service=contact_service,
    api_prefix='/api/contacts',
    required_fields=['name', 'email'],
    unique_fields=['email']
)
logger.info("Contact API routes instantiated successfully.")