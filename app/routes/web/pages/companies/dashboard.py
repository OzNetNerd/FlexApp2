from flask import request
from flask_login import login_required
from app.services.company import CompanyService
from app.routes.web.pages.companies import companies_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

company_service = CompanyService()

@companies_bp.route("/", methods=["GET"], endpoint="index")
@login_required
def companies_dashboard():
    # Get statistics and data from service
    stats = company_service.get_dashboard_stats()
    top_companies = company_service.get_top_companies()
    segments = company_service.get_engagement_segments()
    growth_data = company_service.prepare_growth_data()

    # Create context for the dashboard view
    context = WebContext(
        title="Companies Dashboard",
        read_only=True,
        stats=stats,
        segments=segments,
        top_companies=top_companies,
        growth_data=growth_data
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/companies/dashboard.html",
        context=context,
        error_message="An error occurred while rendering the companies dashboard",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)