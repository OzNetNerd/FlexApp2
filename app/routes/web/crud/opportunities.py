import logging
from flask import Blueprint, request, redirect, url_for
from app.models import Opportunity, Company, db
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import Context
from app.routes.base.crud_factory import register_crud_routes

logger = logging.getLogger(__name__)

# Define the blueprint
opportunities_bp = Blueprint("opportunities", __name__, url_prefix="/opportunities")

# Register standard CRUD routes
register_crud_routes(opportunities_bp, "opportunity")


# Custom route: Create opportunity with company handling
@opportunities_bp.route("/custom-create", methods=["GET", "POST"])
def custom_create():
    """Custom opportunity creation route with company handling."""
    if request.method == "POST":
        form_data = request.form.to_dict()

        # Process company name
        company_name = form_data.get("company_name", "").strip()
        if company_name:
            company = Company.query.filter_by(name=company_name).first()
            if not company:
                logger.info(f"Creating new company: {company_name}")
                company = Company(name=company_name)
                db.session.add(company)
                db.session.commit()
            form_data["company_id"] = company.id

        # Remove invalid model field
        form_data.pop("company_name", None)

        # Validate required fields
        errors = []
        if not form_data.get("name"):
            errors.append("Name is required.")

        if errors:
            context = Context(title="Create Opportunity", errors=errors, form_data=form_data)
            return render_safely("pages/crud/create.html", context, "Failed to create opportunity.")

        opportunity = Opportunity(**form_data)
        db.session.add(opportunity)
        db.session.commit()

        return redirect(url_for("opportunities.view", item_id=opportunity.id))

    context = Context(title="Create Opportunity")
    return render_safely("pages/crud/create.html", context, "Failed to load create opportunity form.")


# Helper: Preprocess form data
def preprocess_opportunity_form(form_data):
    """Process form data for opportunities, handling company relationships."""
    company_name = form_data.get("company_name", "").strip()
    if company_name:
        company = Company.query.filter_by(name=company_name).first()
        if not company:
            logger.info(f"Creating new company: {company_name}")
            company = Company(name=company_name)
            db.session.add(company)
            db.session.commit()
        form_data["company_id"] = company.id

    form_data.pop("company_name", None)
    return form_data


logger.info("Opportunity routes setup successfully.")
