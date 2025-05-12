# app/routes/web/pages/companies/filters.py

from flask import request
from flask_login import login_required
from app.services.company import CompanyService
from app.routes.web.pages.companies import companies_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

company_service = CompanyService()

@companies_bp.route("/filtered", methods=["GET"])
@login_required
def filtered_companies():
    # Get filter parameters
    filters = {
        "has_opportunities": request.args.get("has_opportunities"),
        "has_contacts": request.args.get("has_contacts"),
        "has_capabilities": request.args.get("has_capabilities")
    }

    # Get filtered companies from service
    companies = company_service.get_filtered_companies(filters)

    # Create context for the filtered view
    context = WebContext(
        title="Filtered Companies",
        read_only=True,
        companies=companies,
        filters=filters
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/companies/filtered.html",
        context=context,
        error_message="An error occurred while rendering the filtered companies page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)