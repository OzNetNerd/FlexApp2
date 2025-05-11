from flask import render_template
from flask_login import login_required
from app.services.company_service import CompanyService
from app.routes.web.pages.companies import companies_bp

company_service = CompanyService()


@companies_bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    # Get statistics from service
    stats = company_service.get_statistics()

    return render_template(
        "pages/companies/statistics.html",
        total_companies=stats["total_companies"],
        with_opportunities=stats["with_opportunities"],
        with_contacts=stats["with_contacts"],
        no_engagement=stats["no_engagement"]
    )