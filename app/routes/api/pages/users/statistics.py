# app/routes/api/pages/users/statistics.py

from flask import jsonify
from app.services.user import UserService
from app.routes.api.pages.users import users_api_bp

# Initialize specialized service
user_service = UserService()

@users_api_bp.route("/statistics", methods=["GET"])
def get_statistics():
    """Get comprehensive statistics for the statistics page."""
    stats = user_service.get_statistics()
    return jsonify(stats)