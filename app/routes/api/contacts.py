from app.models import Contact
from app.routes.api import api_contacts_bp
from app.routes.api.generic import GenericAPIRoutes
from app.services.crud_service import CRUDService
import logging

logger = logging.getLogger(__name__)

logger.debug("Instantiating GenericAPIRoutes for the Contact model.")
contact_api_routes = GenericAPIRoutes(
    blueprint=api_contacts_bp,
    model=Contact,
    service=CRUDService(Contact),
    api_prefix='/api/contacts',
    required_fields=['name', 'email'],
    unique_fields=['email']
)
logger.info("Contact API routes instantiated successfully.")