from flask import request
from flask_login import login_required
from app.models.pages.company import Company
from app.services.contact import ContactService
from . import contacts_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

contact_service = ContactService()

@contacts_bp.route("/filtered", methods=["GET"])
@login_required
def filtered_contacts():
    has_opportunities = request.args.get("has_opportunities")
    has_company = request.args.get("has_company")
    skill_level = request.args.get("skill_level")

    contacts = contact_service.get_filtered_contacts(
        has_opportunities=has_opportunities,
        has_company=has_company,
        skill_level=skill_level
    )

    companies = Company.query.order_by(Company.name.asc()).all()

    # Create context for the filtered view
    context = WebContext(
        title="Filtered Contacts",
        read_only=True,
        contacts=contacts,
        companies=companies,
        filters={"has_opportunities": has_opportunities, "has_company": has_company, "skill_level": skill_level}
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/contacts/filtered.html",
        context=context,
        error_message="An error occurred while rendering the filtered contacts page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)