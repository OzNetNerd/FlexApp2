# app/routes/api/pages/companies/statistics.py

from flask import jsonify
from app.services.company import CompanyService
from app.routes.api.pages.companies import companies_api_bp

# Initialize specialized service
company_service = CompanyService()

@companies_api_bp.route("/statistics", methods=["GET"])
def get_statistics():
    """Get comprehensive statistics for the statistics page."""
    stats = company_service.get_statistics()
    return jsonify(stats)