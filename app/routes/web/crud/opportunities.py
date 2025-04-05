import logging
from app.models import Opportunity, Company, db
from app.routes.blueprint_factory import create_blueprint
from app.routes.base.crud_factory import register_crud_routes
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import Context

logger = logging.getLogger(__name__)

# Create blueprint
opportunities_bp = create_blueprint("opportunities")

# Register standard CRUD routes
register_crud_routes(opportunities_bp, "opportunity")


# Add custom route handlers
@opportunities_bp.route('/custom-create', methods=['GET', 'POST'])
def custom_create():
    """Custom opportunity creation route with company handling."""
    from flask import request, redirect, url_for

    if request.method == 'POST':
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

        # Remove 'company_name' as it's not a valid model field
        form_data.pop("company_name", None)

        # Validate required fields
        errors = []
        if not form_data.get("name"):
            errors.append("Name is required.")

        if errors:
            context = Context(title="Create Opportunity", errors=errors, form_data=form_data)
            return render_safely("pages/crud/create.html", context, "Failed to create opportunity.")

        # Create opportunity
        opportunity = Opportunity(**form_data)
        db.session.add(opportunity)
        db.session.commit()

        return redirect(url_for('opportunities.view', item_id=opportunity.id))

    # GET request
    context = Context(title="Create Opportunity")
    return render_safely("pages/crud/create.html", context, "Failed to load create opportunity form.")


# Helper function to preprocess opportunity form data
def preprocess_opportunity_form(form_data):
    """Process form data for opportunities, handling company relationships."""
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

    # Remove 'company_name' as it's not a valid model field
    form_data.pop("company_name", None)
    return form_data