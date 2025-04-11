# api/companies.py

import logging
from flask import Blueprint
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig
from app.models.company import Company
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)

# Define the blueprint
companies_api_bp = Blueprint("companies_api", __name__, url_prefix="/api/companies")

company_service = CRUDService(Company)

# Register all standard CRUD API routes
company_api_crud_config = ApiCrudRouteConfig(
    blueprint=companies_api_bp,
    entity_table_name="Company",
    service=company_service
)
register_api_crud_routes(company_api_crud_config)

logger.info("Successfully set up 'Company' API routes.")