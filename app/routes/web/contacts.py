import re
from models import Contact, Company, db
from routes.web import contacts_bp
from routes.web.generic import GenericWebRoutes
import logging

logger = logging.getLogger(__name__)


class ContactCRUDRoutes(GenericWebRoutes):
    """
    Custom CRUD routes for Contacts model that extends the generic implementation
    """

    def _preprocess_form_data(self, form_data):
        """
        Convert company_name to company_id, create company if it doesn't exist,
        and remove company_name from the data passed to the model.
        """
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

        # 🔥 Remove the field that does not exist on the model
        form_data.pop('company_name', None)

    def _validate_create(self, form_data):
        """
        Override validation for creating a contact
        """
        self._preprocess_form_data(form_data)
        errors = super()._validate_create(form_data)
        self._validate_contact_data(form_data, errors)
        return errors

    def _validate_edit(self, item, form_data):
        """
        Override validation for editing a contact
        """
        self._preprocess_form_data(form_data)
        errors = super()._validate_edit(item, form_data)
        self._validate_contact_data(form_data, errors)
        return errors

    def _validate_contact_data(self, form_data, errors):
        """
        Common validation for contact data
        """
        # Email validation
        if form_data.get('email'):
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, form_data['email']):
                errors.append('Invalid email format')
                logger.warning(f"Invalid email format: {form_data['email']}")


# Set up the CRUD routes for contacts
logger.debug("Setting up CRUD routes for contacts.")
contact_routes = ContactCRUDRoutes(
    blueprint=contacts_bp,
    model=Contact,
    index_template='contacts.html',
    required_fields=['first_name', 'last_name'],
    unique_fields=['email']
)

