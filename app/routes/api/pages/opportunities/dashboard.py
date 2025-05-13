# app/routes/api/pages/opportunities/dashboard.py

from flask import jsonify, request
from app.services.opportunity import OpportunityService
from app.routes.api.pages.opportunities import opportunities_api_bp

# Initialize specialized service
opportunity_service = OpportunityService()


@opportunities_api_bp.route("/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """Get statistics for the opportunities dashboard."""
    stats = opportunity_service.get_dashboard_stats()
    return jsonify(stats)


@opportunities_api_bp.route("/dashboard/top", methods=["GET"])
def get_top_opportunities():
    """Get top opportunities by value."""
    limit = request.args.get("limit", 5, type=int)
    top_opportunities = opportunity_service.get_top_opportunities(limit)

    # Convert SQLAlchemy objects to dict for JSON serialization
    result = []
    for opportunity, value in top_opportunities:
        opportunity_dict = opportunity.to_dict()
        opportunity_dict["value"] = value
        result.append(opportunity_dict)

    return jsonify(result)


@opportunities_api_bp.route("/dashboard/segments", methods=["GET"])
def get_stage_segments():
    """Get opportunity segments by stage."""
    segments = opportunity_service.get_stage_segments()
    return jsonify(segments)


@opportunities_api_bp.route("/dashboard/growth", methods=["GET"])
def get_growth_data():
    """Get growth data for the chart."""
    months_back = request.args.get("months_back", 6, type=int)
    growth_data = opportunity_service.prepare_growth_data(months_back)
    return jsonify(growth_data)
