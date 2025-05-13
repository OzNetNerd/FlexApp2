# app/routes/api/pages/srs/stats.py

from flask import jsonify, request
from app.services.srs import SRSService
from app.routes.api.pages.srs import srs_api_bp

# Initialize service
srs_service = SRSService()


@srs_api_bp.route("/stats", methods=["GET"])
def get_srs_stats():
    """Get current SRS system statistics."""
    return srs_service.get_stats()


@srs_api_bp.route("/progress-data", methods=["GET"])
def progress_data():
    """Get progress data for charts."""
    months = request.args.get("months", 7, type=int)
    data = srs_service.get_learning_progress_data(months=months)
    return jsonify(data)
