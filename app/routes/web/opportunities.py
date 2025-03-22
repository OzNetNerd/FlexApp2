from models import Opportunity, Company, db
from routes.web import opportunities_bp
from routes.web.generic import GenericWebRoutes
from services.crud_service import CRUDService
import logging
import re

logger = logging.getLogger(__name__)


class OpportunityCRUDRoutes(GenericWebRoutes):
    """
    Custom CRUD routes for Opportunity model.
    """

    def _build_fields(self, item=None):
        logger.debug("Building fields for opportunity form")
        fields = [
            {
                'name': 'name',
                'label': 'Name',
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
                'section': 'Details'
            },
            {
                'name': 'value',
                'label': 'Value',
                'type': 'number',
                'value': getattr(item, 'value', '') if item else '',
                'section': 'Details'
            },
            {
                'name': 'status',
                'label': 'Status',
                'type': 'select',
                'value': getattr(item, 'status', '') if item else '',
                'options': [
                    {'value': 'new', 'label': 'New'},
                    {'value': 'qualified', 'label': 'Qualified'},
                    {'value': 'won', 'label': 'Won'},
                    {'value': 'lost', 'label': 'Lost'}
                ],
                'section': 'Details'
            },
            {
                'name': 'company_name',
                'label': 'Company',
                'type': 'text',
                'value': item.company.name if item and item.company else '',
                'section': 'Company Info'
            }
        ]
        return fields

    def _preprocess_form_data(self, form_data):
        company_name = form_data.get('company_name', '').strip()
        if company_name:
            company = Company.query.filter_by(name=company_name).first()
            if not company:
                logger.info(f"Creating new company: {company_name}")
                company = Company(name=company_name)
                db.session.add(company)
                db.session.commit()
            form_data['company_id'] = company.id
        else:
            form_data['company_id'] = None

        # Remove 'company_name' as it's not a valid model field
        form_data.pop('company_name', None)

    def _validate_create(self, form_data):
        self._preprocess_form_data(form_data)
        return super()._validate_create(form_data)

    def _validate_edit(self, item, form_data):
        self._preprocess_form_data(form_data)
        return super()._validate_edit(item, form_data)

opportunity_routes = OpportunityCRUDRoutes(
    blueprint=opportunities_bp,
    model=Opportunity,
    service=CRUDService(),
    index_template='opportunities.html',
    create_template='opportunities/create.html',
    edit_template='opportunities/edit.html',
    view_template='base/base-view.html',
    required_fields=['name'],
    unique_fields=[]
)
