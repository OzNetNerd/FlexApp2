import re
import logging
from flask_login import current_user
from app.models import Contact, Company, db, User, CRISPScore
from app.routes.blueprint_factory import create_blueprint
from app.routes.base.crud_factory import register_crud_routes
from app.routes.base.components.entity_handler import Context
from app.routes.base.components.template_renderer import render_safely

logger = logging.getLogger(__name__)

# Create blueprint
contacts_bp = create_blueprint("contacts")

# Register standard CRUD routes
register_crud_routes(contacts_bp, "contact")


# Add custom route handlers
@contacts_bp.route('/<int:item_id>/view-extended')
def view_extended(item_id):
    """View contact with additional relationship and CRISP score information."""
    contact = Contact.query.get_or_404(item_id)

    # Set up context
    context = Context(title=f"View Contact: {contact.first_name} {contact.last_name}", item_id=item_id)

    # Add relationship and CRISP scores
    relationship = contact.get_relationship_with(current_user)
    context.relationship = relationship

    if relationship:
        context.crisp_scores = relationship.crisp_scores.order_by(CRISPScore.created_at.desc()).all()

    return render_safely("pages/crud/view.html", context, "Failed to load contact details.")


# Preprocessing for form data
def preprocess_contact_form(form_data):
    """
    Convert company_name to company_id, create company if needed,
    and handle user associations.
    """
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
    user_ids = form_data.get("users", [])
    if isinstance(user_ids, str):
        user_ids = [user_ids]

    if user_ids:
        users = User.query.filter(User.id.in_(user_ids)).all()
        form_data["users"] = users
        logger.info(f"👥 Linked users: {[u.email for u in users]}")

    return form_data


# Validation for contact data
def validate_contact_data(form_data):
    """Validate contact form data and return any errors."""
    errors = []

    # Check required fields
    for field in ["first_name", "last_name"]:
        if not form_data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required.")

    # Check email format
    if form_data.get("email"):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, form_data["email"]):
            errors.append("Invalid email format")
            logger.warning(f"❌ Invalid email format: {form_data['email']}")

    # Check email uniqueness
    if form_data.get("email"):
        existing = Contact.query.filter_by(email=form_data["email"]).first()
        if existing and (not form_data.get("id") or existing.id != int(form_data["id"])):
            errors.append(f"Email '{form_data['email']}' is already in use.")

    return errors

# Add route overrides for custom form processing if needed
# Example:
# @contacts_bp.route('/create', methods=['POST'])
# def create_contact():
#     # Custom creation logic