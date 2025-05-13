# app/routes/api/pages/opportunities/filters.py

from flask import jsonify, request
from app.services.opportunity import OpportunityService
from app.routes.api.pages.opportunities import opportunities_api_bp

# Initialize specialized service
opportunity_service = OpportunityService()


@opportunities_api_bp.route("/filtered", methods=["GET"])
def get_filtered_opportunities():
    """Get opportunities based on filter criteria."""
    filters = {
        "stage": request.args.get("stage"),
        "has_company": request.args.get("has_company"),
        "has_contacts": request.args.get("has_contacts"),
        "min_value": request.args.get("min_value"),
    }
    opportunities = opportunity_service.get_filtered_opportunities(filters)

    # Convert SQLAlchemy objects to dict for JSON serialization
    result = [opportunity.to_dict() for opportunity in opportunities]

    return jsonify(result)
