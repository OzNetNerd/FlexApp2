# app/routes/companies.py
import logging
from flask import Blueprint
from app.routes.web.route_registration import register_crud_routes, CrudRouteConfig, CrudTemplates
from app.services.crud_service import CRUDService
from app.models.company import Company

logger = logging.getLogger(__name__)

# Define the blueprint
companies_bp = Blueprint("companies_bp", __name__, url_prefix="/companies")

# Create a service instance
company_service = CRUDService(Company)

# Define custom templates
custom_templates = CrudTemplates(
    # The route_type here is "view", so the template file is named accordingly.
    # create="pages/crud/create_view_edit_company.html",
    create="pages/crud/create_view_edit_company.html",
    view="pages/crud/create_view_edit_company.html",
    edit="pages/crud/create_view_edit_company.html",
)

# Add debug logging to verify templates are set correctly
logger.info(f"Custom templates: {custom_templates.to_dict()}")

# Register all standard CRUD routes with custom templates
company_crud_config = CrudRouteConfig(
    blueprint=companies_bp, entity_table_name="Company", service=company_service, templates=custom_templates
)
register_crud_routes(company_crud_config)
