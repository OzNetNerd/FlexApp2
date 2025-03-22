import logging
from models import Company
from routes.web import companies_bp
from routes.web.generic import GenericWebRoutes

logger = logging.getLogger(__name__)

class CompanyCRUDRoutes(GenericWebRoutes):
    pass

company_routes = CompanyCRUDRoutes(
    blueprint=companies_bp,
    model=Company,
    required_fields=['name'],
    unique_fields=['name'],  # ✅ Prevent duplicates
    index_template='companies.html',
)
