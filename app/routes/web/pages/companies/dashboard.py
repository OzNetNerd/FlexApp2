from flask import render_template
from flask_login import login_required
from app.services.company_service import CompanyService
from app.routes.web.pages.companies import companies_bp

company_service = CompanyService()

@companies_bp.route("/", methods=["GET"], endpoint="index")
@login_required
def companies_dashboard():
    # Get statistics and data from service
    stats = company_service.get_dashboard_stats()
    top_companies = company_service.get_top_companies()
    segments = company_service.get_engagement_segments()
    growth_data = company_service.prepare_growth_data()

    return render_template(
        "pages/companies/dashboard.html",
        stats=stats,
        segments=segments,
        top_companies=top_companies,
        growth_data=growth_data
    )