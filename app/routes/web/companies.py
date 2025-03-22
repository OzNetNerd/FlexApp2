import logging
from models import Company
from routes.web import companies_bp
from routes.web.generic import GenericWebRoutes

logger = logging.getLogger(__name__)

class CompanyCRUDRoutes(GenericWebRoutes):
    def _build_fields(self, item=None):
        logger.debug("Building fields for company form")
        return [
            {
                'name': 'name',
                'label': 'Company Name',
                'type': 'text',
                'value': getattr(item, 'name', '') if item else '',
                'required': True,
                'section': 'Basic Info'
            },
            {
                'name': 'description',
                'label': 'Description',
                'type': 'textarea',
                'value': getattr(item, 'description', '') if item else '',
                'required': False,
                'section': 'Basic Info'
            }
        ]

company_routes = CompanyCRUDRoutes(
    blueprint=companies_bp,
    model=Company,
    required_fields=['name'],
    unique_fields=['name'],  # ✅ Prevent duplicates
    index_template='companies.html',
    view_template='base/base-view.html',
    create_template='companies/create.html',
    edit_template='companies/edit.html',
)
