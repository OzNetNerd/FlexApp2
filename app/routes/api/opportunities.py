from app.models import Opportunity
from app.routes.api import api_opportunities_bp
from app.routes.api.generic import GenericAPIRoutes
from app.services.crud_service import CRUDService
import logging

logger = logging.getLogger(__name__)

logger.debug("Instantiating GenericAPIRoutes for the Opportunity model.")
opportunity_api_routes = GenericAPIRoutes(
    blueprint=api_opportunities_bp,
    model=Opportunity,
    service=CRUDService(Opportunity),
    api_prefix="/api/opportunities",
    required_fields=["name"],
    unique_fields=[],
)
logger.info("Opportunity API routes instantiated successfully.")
