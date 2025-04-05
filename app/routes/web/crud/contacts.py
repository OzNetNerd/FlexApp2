import re
import logging
from flask import Blueprint, abort, render_template
from flask_login import current_user

from app.models import Contact, Company, db, User, CRISPScore
from app.routes.web.crud.components.generic_crud_routes import GenericWebRoutes
from app.routes.base.components.entity_handler import Context
from app.routes.base.components.template_renderer import render_safely

logger = logging.getLogger(__name__)

# Define the blueprint
contacts_bp = Blueprint("contacts", __name__, url_prefix="/contacts")


class ContactsCRUDRoutes(GenericWebRoutes):
    """
    Custom CRUD routes for Contact model.
    """

    def _preprocess_form_data(self, form_data):
        return preprocess_contact_form(form_data)

    def _validate_form_data(self, form_data):
        return validate_contact_data(form_data)

    def index(self):
        """Overrides the default index for Contacts."""
        if not current_user.is_authenticated:
            abort(403)

        return render_template(
            self.index_template,
            title="Contacts",
        )


# Register the CRUD route handler
contacts_routes = ContactsCRUDRoutes(
    blueprint=contacts_bp,
    model=Contact,
    index_template="pages/tables/contacts.html",
    required_fields=[],
    unique_fields=[],
)


# Custom route: View contact with extra context
@contacts_bp.route("/<int:item_id>/view-extended")
def view_extended(item_id):
    """View contact with additional relationship and CRISP score information."""
    contact = Contact.query.get_or_404(item_id)

    context = Context(title=f"View Contact: {contact.first_name} {contact.last_name}", item_id=item_id)

    relationship = contact.get_relationship_with(current_user)
    context.relationship = relationship

    if relationship:
        context.crisp_scores = relationship.crisp_scores.order_by(CRISPScore.created_at.desc()).all()

    return render_safely("pages/crud/view.html", context, "Failed to load contact details.")


# Helper: Preprocess form data
def preprocess_contact_form(form_data):
    """
    Convert company_name to company_id, create company if needed,
    and handle user associations.
    """
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

    user_ids = form_data.get("users", [])
    if isinstance(user_ids, str):
        user_ids = [user_ids]

    if user_ids:
        users = User.query.filter(User.id.in_(user_ids)).all()
        form_data["users"] = users
        logger.info(f"👥 Linked users: {[u.email for u in users]}")

    return form_data


# Helper: Validate contact data
def validate_contact_data(form_data):
    """Validate contact form data and return any errors."""
    errors = []

    for field in ["first_name", "last_name"]:
        if not form_data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required.")

    if form_data.get("email"):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, form_data["email"]):
            errors.append("Invalid email format")
            logger.warning(f"❌ Invalid email format: {form_data['email']}")

        existing = Contact.query.filter_by(email=form_data["email"]).first()
        if existing and (not form_data.get("id") or existing.id != int(form_data["id"])):
            errors.append(f"Email '{form_data['email']}' is already in use.")

    return errors


logger.info("Contact routes setup successfully.")
