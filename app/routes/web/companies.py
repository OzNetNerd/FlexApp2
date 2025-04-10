# At the top of companies.py
import logging

# Example 1: Full CRUD Entity
# app/routes/companies.py
from flask import Blueprint
from app.routes.base.web_utils import register_crud_routes
from app.services.crud_service import CRUDService
from app.models.company import Company
from app.routes.base.web_utils import CrudRouteConfig
import logging

logger = logging.getLogger(__name__)
# Define the blueprint
companies_bp = Blueprint("companies_bp", __name__, url_prefix="/companies")

# Create a service instance
company_service = CRUDService(Company)

# Register all standard CRUD routes
company_crud_config = CrudRouteConfig(blueprint=companies_bp, entity_table_name="Company", service=company_service)
register_crud_routes(company_crud_config)