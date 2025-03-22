from app.models import Company
from app.routes.api import api_companies_bp
from app.routes.api.generic import GenericAPIRoutes
from app.services.crud_service import CRUDService
import logging

logger = logging.getLogger(__name__)

# API routes
company_service = CRUDService()
logger.debug("Instantiating GenericAPIRoutes for the Company model.")
company_api_routes = GenericAPIRoutes(
   blueprint=api_companies_bp,
   model=Company,
   service=company_service,
   api_prefix='/api/companies',
   required_fields=['name'],
   unique_fields=['name']
)
logger.info("Company API routes instantiated successfully.")