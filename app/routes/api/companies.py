# app/routes/api/companies.py

from flask import Blueprint
from app.utils.app_logging import get_logger
from app.services.crud_service import CRUDService
from app.models import Company
from app.routes.api.route_registration import ApiCrudRouteConfig

logger = get_logger()

ENTITY_NAME = "Company"
ENTITY_PLURAL_NAME = "Companies"

companies_api_bp = Blueprint(f"{ENTITY_PLURAL_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

company_service = CRUDService(Company)

company_api_crud_config = ApiCrudRouteConfig(blueprint=companies_api_bp, entity_table_name=ENTITY_NAME, service=company_service)
