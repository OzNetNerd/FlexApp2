# app/routes/api/pages/users/filters.py

from flask import jsonify, request
from app.services.user import UserService
from app.routes.api.pages.users import users_api_bp

# Initialize specialized service
user_service = UserService()


@users_api_bp.route("/filtered", methods=["GET"])
def get_filtered_users():
    """Get users based on filter criteria."""
    filters = {"role": request.args.get("role"), "active": request.args.get("active"), "department": request.args.get("department")}
    users = user_service.get_filtered_users(filters)
    return jsonify([user.to_dict() for user in users])
