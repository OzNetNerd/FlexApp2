# app/routes/web/companies.py

from flask import Blueprint
from app.utils.app_logging import get_logger
from app.services.crud_service import CRUDService
from app.models import Company
from app.routes.web.route_registration import CrudRouteConfig, default_crud_templates

logger = get_logger()

companies_bp = Blueprint("companies_bp", __name__, url_prefix="/companies")

company_service = CRUDService(Company)

# Use the centralized factory instead of hard-coding paths
templates = default_crud_templates("Company")

company_crud_config = CrudRouteConfig(
    blueprint=companies_bp,
    entity_table_name="Company",
    service=company_service,
    templates=templates,
)
