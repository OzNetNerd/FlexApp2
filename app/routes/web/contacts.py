import re
import logging
from flask import request
from flask_login import current_user
from app.models import Contact, Company, db, User
from app.routes.web import contacts_bp
from app.routes.web.generic import GenericWebRoutes

logger = logging.getLogger(__name__)


class ContactCRUDRoutes(GenericWebRoutes):
    """
    Custom CRUD routes for Contacts model that extends the generic implementation.
    """

    def add_view_context(self, item, context):
        from app.models import Relationship, CRISPScore

        user = current_user
        relationship = item.get_relationship_with(user)
        context["relationship"] = relationship

        if relationship:
            context["crisp_scores"] = relationship.crisp_scores.order_by(CRISPScore.created_at.desc()).all()

    def _preprocess_form_data(self, request_obj):
        """
        Convert company_name to company_id, create company if needed,
        and extract user associations using request.form.getlist().

        Args:
            request_obj (flask.Request): The full Flask request object.

        Returns:
            dict: Preprocessed form data with company_id and user objects.
        """
        form_data = request_obj.form.to_dict(flat=True)

        # Handle company name → ID
        company_name = form_data.get("company_name", "").strip()
        if company_name:
            company = Company.query.filter_by(name=company_name).first()
            if not company:
                logger.info(f"🏢 Creating new company: {company_name}")
                company = Company(name=company_name)
                db.session.add(company)
                db.session.commit()
            form_data["company_id"] = company.id
        else:
            form_data["company_id"] = None

        form_data.pop("company_name", None)

        # Handle user IDs from multi-select
        user_ids = request_obj.form.getlist("users")
        if user_ids:
            users = User.query.filter(User.id.in_(user_ids)).all()
            form_data["users"] = users
            logger.info(f"👥 Linked users: {[u.email for u in users]}")

        return form_data

    def _validate_create(self, form_data):
        """
        Core validation for creating a contact from dict form data.
        """
        errors = super()._validate_create(form_data)
        self._validate_contact_data(form_data, errors)
        return errors

    def _validate_edit(self, item, request_obj):
        """
        Entry point from GenericWebRoutes that expects a Flask request object.
        Converts to dict before calling actual validation logic.
        """
        form_data = self._preprocess_form_data(request_obj)
        return self._validate_edit_data(item, form_data)

    def _validate_edit_data(self, item, form_data):
        """
        Core validation for editing a contact from preprocessed form data.
        """
        errors = super()._validate_edit(item, form_data)
        self._validate_contact_data(form_data, errors)
        return errors

    def _validate_contact_data(self, form_data, errors):
        """
        Common validation for contact data.
        """
        if form_data.get("email"):
            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_regex, form_data["email"]):
                errors.append("Invalid email format")
                logger.warning(f"❌ Invalid email format: {form_data['email']}")


# Set up the CRUD routes for contacts
logger.debug("⚙️ Setting up CRUD routes for contacts.")
contact_routes = ContactCRUDRoutes(
    blueprint=contacts_bp,
    model=Contact,
    index_template="contacts.html",
    required_fields=["first_name", "last_name"],
    unique_fields=["email"],
)
