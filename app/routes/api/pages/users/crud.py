# app/routes/api/pages/users/crud.py

from flask import jsonify, request
from app.models import User
from app.services.user import UserService
from app.routes.api.pages.users import users_api_bp
from app.routes.api.route_registration import ApiCrudRouteConfig
from app.utils.app_logging import get_logger

logger = get_logger()

# Register CRUD service and config - using specialized UserService
user_service = UserService(User)
user_api_crud_config = ApiCrudRouteConfig(blueprint=users_api_bp, entity_table_name="User", service=user_service)


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

# For users
@users_api_bp.route("/<int:user_id>", methods=["PATCH"])
def update_user_field(user_id):
    """Update a single field of a user."""
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No update data provided"}), 400

        logger.info(f"Updating user {user_id} with data: {data}")

        # Get current user to validate it exists
        user = user_service.get_by_id(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        # Update only provided fields
        updated_user = user_service.update(user, data)
        return jsonify(updated_user.to_dict())
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        return jsonify({"error": f"Failed to update: {str(e)}"}), 500