import re
import logging
from flask_login import current_user
from app.models import Contact, Company, db, User
from app.routes.web import contacts_bp
from app.routes.web.generic_crud_routes import GenericWebRoutes
from typing import Any, Dict, List
from app.models import CRISPScore

logger = logging.getLogger(__name__)


class ContactCRUDRoutes(GenericWebRoutes):
    """
    Custom CRUD routes for Contacts model that extends the generic implementation.
    """

    @staticmethod
    def add_view_context(item: Any, context: Dict[str, Any]) -> None:
        """Adds relationship and CRISP score information to the view context.

        This method retrieves the relationship between the current user and the provided item.
        It then adds the relationship to the context dictionary. If a relationship exists,
        the method further queries for the associated CRISP scores, ordered by their creation
        date in descending order, and adds these scores to the context.

        Args:
            item (Any): An object representing an item that supports a relationship with the current user.
                This object must implement a `get_relationship_with` method that accepts a user.
            context (Dict[str, Any]): A dictionary that will be updated with view context data. The keys
                'relationship' and 'crisp_scores' (if applicable) will be added to this dictionary.

        Returns:
            None: The function modifies the `context` dictionary in place.
        """

        relationship = item.get_relationship_with(current_user)
        context["relationship"] = relationship

        if relationship:
            context["crisp_scores"] = relationship.crisp_scores.order_by(CRISPScore.created_at.desc()).all()

    def _preprocess_form_data(self, request_obj):
        """
        Convert company_name to company_id, create company if needed,
        and extract user associations using request.form.getlist().

        Args:
            request_obj (flask.Request or dict): The full Flask request object or a pre-parsed form dict.

        Returns:
            dict: Preprocessed form data with company_id and user objects.
        """
        # Determine if request_obj is a Flask request or a dict
        if isinstance(request_obj, dict):
            form_data = request_obj

            # Define a simple getlist function for dicts
            def getlist(key):
                # In case the dict already has a list or a single value
                value = form_data.get(key)
                if isinstance(value, list):
                    return value
                return [value] if value is not None else []
        else:
            form_data = request_obj.form.to_dict(flat=True)
            getlist = request_obj.form.getlist

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
        user_ids = getlist("users")
        if user_ids:
            users = User.query.filter(User.id.in_(user_ids)).all()
            form_data["users"] = users
            logger.info(f"👥 Linked users: {[u.email for u in users]}")

        return form_data

    def _validate_create(self, form_data: Dict[str, Any]) -> List[str]:
        """Core validation for creating a contact from dictionary form data.

        This method performs the primary validation for creating a contact. It delegates to
        the parent class's validation method and then performs additional checks for the
        contact data.

        Args:
            form_data (Dict[str, Any]): A dictionary containing form data for creating a contact.

        Returns:
            List[str]: A list of validation error messages (if any).
        """
        errors = super()._validate_create(form_data)
        self._validate_contact_data(form_data, errors)
        return errors

    def _validate_edit(self, item: Any, request_obj: Any) -> List[str]:
        """Entry point from GenericWebRoutes that expects a Flask request object.

        This method converts the Flask request object to a dictionary and then calls
        the actual validation logic for editing a contact.

        Args:
            item (Any): The item (contact) to be edited.
            request_obj (Any): The Flask request object containing the form data.

        Returns:
            List[str]: A list of validation error messages (if any).
        """
        form_data = self._preprocess_form_data(request_obj)
        return self._validate_edit_data(item, form_data)

    def _validate_edit_data(self, item: Any, form_data: Dict[str, Any]) -> List[str]:
        """Core validation for editing a contact from preprocessed form data.

        This method performs the primary validation for editing a contact. It delegates
        to the parent class's validation method and then performs additional checks for
        the contact data.

        Args:
            item (Any): The item (contact) to be edited.
            form_data (Dict[str, Any]): A dictionary containing preprocessed form data for editing a contact.

        Returns:
            List[str]: A list of validation error messages (if any).
        """
        errors = super()._validate_edit(item, form_data)
        self._validate_contact_data(form_data, errors)
        return errors

    @staticmethod
    def _validate_contact_data(form_data: Dict[str, Any], errors: List[str]) -> None:
        """Common validation for contact data.

        This method validates the contact data, specifically checking if the email format is valid.

        Args:
            form_data (Dict[str, Any]): A dictionary containing form data for a contact.
            errors (List[str]): A list of error messages that will be populated with validation errors.

        Returns:
            None: The function modifies the `errors` list in place.
        """
        if form_data.get("email"):
            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_regex, form_data["email"]):
                errors.append("Invalid email format")
                logger.warning(f"❌ Invalid email format: {form_data['email']}")


# Set up CRUD routes for managing contacts within the 'contacts_bp' blueprint.
# This configures routes for creating, reading, updating, and deleting contacts.
# The setup includes:
# - The `Contact` model as the target for CRUD operations.
# - The template used for rendering the contacts table: `entity_tables/contacts.html`.
# - Required fields for contact creation: `first_name` and `last_name`.
# - A uniqueness constraint on the `email` field to prevent duplicate entries.
logger.debug("⚙️ Setting up CRUD routes for contacts.")
contact_routes = ContactCRUDRoutes(
    blueprint=contacts_bp,
    model=Contact,
    index_template="entity_tables/contacts.html",
    required_fields=["first_name", "last_name"],
    unique_fields=["email"],
)
