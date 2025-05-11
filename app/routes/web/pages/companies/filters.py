from flask import render_template, request
from flask_login import login_required
from app.services.company_service import CompanyService
from app.routes.web.pages.companies import companies_bp

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

    return render_template(
        "pages/companies/filtered.html",
        companies=companies,
        filters=filters
    )