# api/companies.py

from flask import Blueprint
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig
from app.models.company import Company
from app.services.crud_service import CRUDService

from app.utils.app_logging import get_logger
logger = get_logger()

ENTITY_NAME = "Company"
ENTITY_PLURAL_NAME = "Companies"

companies_api_bp = Blueprint(f"{ENTITY_PLURAL_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")
company_service = CRUDService(Company)

# Register all standard CRUD API routes
company_api_crud_config = ApiCrudRouteConfig(blueprint=companies_api_bp, entity_table_name=ENTITY_NAME, service=company_service)
register_api_crud_routes(company_api_crud_config)

logger.info(f"Successfully set up '{ENTITY_NAME}' API routes.")
