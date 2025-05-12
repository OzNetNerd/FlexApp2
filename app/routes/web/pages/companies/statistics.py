# app/routes/web/pages/companies/statistics.py

from flask import request
from flask_login import login_required
from app.services.company import CompanyService
from app.routes.web.pages.companies import companies_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

company_service = CompanyService()

@companies_bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    # Get statistics from service
    stats = company_service.get_statistics()

    # Create context for the statistics view
    context = WebContext(
        title="Company Statistics",
        read_only=True,
        total_companies=stats["total_companies"],
        with_opportunities=stats["with_opportunities"],
        with_contacts=stats["with_contacts"],
        no_engagement=stats["no_engagement"]
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/companies/statistics.html",
        context=context,
        error_message="An error occurred while rendering the company statistics page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)