# app/routes/api/pages/users/crud.py

from flask import jsonify, request
from app.models import User
from app.services.user import UserService
from app.routes.api.pages.users import users_api_bp
from app.routes.api.route_registration import ApiCrudRouteConfig

# Register CRUD service and config - using specialized UserService
user_service = UserService(User)
user_api_crud_config = ApiCrudRouteConfig(
    blueprint=users_api_bp,
    entity_table_name="User",
    service=user_service
)

@users_api_bp.route("/", methods=["GET"])
def get_all():
    """Get all users."""
    users = user_service.get_all()
    return jsonify([user.to_dict() for user in users])

@users_api_bp.route("/<int:user_id>", methods=["GET"])
def get(user_id):
    """Get a user by ID."""
    user = user_service.get_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())