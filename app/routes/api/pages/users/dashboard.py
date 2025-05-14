# app/routes/api/pages/users/dashboard.py

from flask import jsonify, request
from app.services.user import UserService
from app.routes.api.pages.users import users_api_bp

# Initialize specialized service
user_service = UserService()


@users_api_bp.route("/dashboard/stats", methods=["GET"])
def get_dashboard_statistics():
    """Get statistics for the users dashboard."""
    stats = user_service.get_dashboard_statistics()
    return jsonify(stats)


@users_api_bp.route("/dashboard/active", methods=["GET"])
def get_active_users():
    """Get active users."""
    limit = request.args.get("limit", 10, type=int)
    active_users = user_service.get_most_active_users(limit)
    return jsonify([user.to_dict() for user in active_users])


@users_api_bp.route("/dashboard/recent", methods=["GET"])
def get_recent_users():
    """Get recently added users."""
    limit = request.args.get("limit", 5, type=int)
    recent_users = user_service.get_recently_added_users(limit)
    return jsonify([user.to_dict() for user in recent_users])
