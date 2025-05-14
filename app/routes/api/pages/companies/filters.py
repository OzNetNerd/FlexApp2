# app/routes/api/pages/companies/filters.py

from flask import jsonify, request
from app.services.company import CompanyService
from app.routes.api.pages.companies import companies_api_bp

# Initialize specialized service
company_service = CompanyService()


@companies_api_bp.route("/filtered", methods=["GET"])
def get_filtered_companies():
    """Get companies based on filter criteria."""
    filters = {
        "has_opportunities": request.args.get("has_opportunities"),
        "has_contacts": request.args.get("has_contacts"),
        "has_capabilities": request.args.get("has_capabilities"),
    }
    companies = company_service.get_filtered_entities(filters)

    # Convert SQLAlchemy objects to dict for JSON serialization
    result = [company.to_dict() for company in companies]

    return jsonify(result)
