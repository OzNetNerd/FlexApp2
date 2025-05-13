# app/routes/api/pages/opportunities/statistics.py

from flask import jsonify
from app.services.opportunity import OpportunityService
from app.routes.api.pages.opportunities import opportunities_api_bp

# Initialize specialized service
opportunity_service = OpportunityService()

@opportunities_api_bp.route("/statistics", methods=["GET"])
def get_statistics():
    """Get comprehensive statistics for the statistics page."""
    stats = opportunity_service.get_statistics()
    return jsonify(stats)