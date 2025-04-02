import logging
from app.models import Company
from app.routes.web import companies_bp
from app.routes.web.generic import GenericWebRoutes
from routes.base.ui.companies import get_company_tabs

logger = logging.getLogger(__name__)


class CompanyCRUDRoutes(GenericWebRoutes):
    pass


company_routes = CompanyCRUDRoutes(
    blueprint=companies_bp,
    model=Company,
    required_fields=["name"],
    unique_fields=["name"],  # ✅ Prevent duplicates
    index_template="entity_tables/companies.html",
    create_tabs_function=get_company_tabs,
)
