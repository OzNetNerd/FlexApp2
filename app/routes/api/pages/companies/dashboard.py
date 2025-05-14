# app/routes/api/pages/companies/dashboard.py

from flask import jsonify, request
from app.services.company import CompanyService
from app.routes.api.pages.companies import companies_api_bp

# Initialize specialized service
company_service = CompanyService()


@companies_api_bp.route("/dashboard/stats", methods=["GET"])
def get_dashboard_statistics():
    """Get statistics for the companies dashboard."""
    stats = company_service.get_dashboard_statistics()
    return jsonify(stats)


@companies_api_bp.route("/dashboard/top", methods=["GET"])
def get_top_companies():
    """Get top companies by opportunity count."""
    limit = request.args.get("limit", 5, type=int)
    top_companies = company_service.get_top_companies(limit)

    # Convert SQLAlchemy objects to dict for JSON serialization
    result = []
    for company, count in top_companies:
        company_dict = company.to_dict()
        company_dict["opportunity_count"] = count
        result.append(company_dict)

    return jsonify(result)


@companies_api_bp.route("/dashboard/segments", methods=["GET"])
def get_engagement_segments():
    """Get company segments by engagement level."""
    segments = company_service.get_engagement_segments()
    return jsonify(segments)


@companies_api_bp.route("/dashboard/growth", methods=["GET"])
def get_growth_data():
    """Get growth data for the chart."""
    months_back = request.args.get("months_back", 6, type=int)
    growth_data = company_service.prepare_growth_data(months_back)
    return jsonify(growth_data)
