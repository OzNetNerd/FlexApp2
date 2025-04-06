import logging
from flask import jsonify, request
from app.routes.blueprint_factory import create_blueprint
from app.models import User
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

# Create API blueprint with /api prefix for users
users_api_bp = create_blueprint("api_users", url_prefix="/api/users")
user_service = UserService(User)

@users_api_bp.route("/", methods=["GET"])
def get_all_users():
    """Get all users."""
    users = user_service.get_all()
    return jsonify([user.to_dict() for user in users])

@users_api_bp.route("/<int:item_id>", methods=["GET"])
def get_user(item_id):
    """Get a specific user."""
    user = user_service.get_by_id(item_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())

@users_api_bp.route("/", methods=["POST"])
def create_user():
    """Create a new user."""
    data = request.get_json()
    # Validate required fields
    for field in ["username", "email", "password"]:
        if field not in data:
            return jsonify({"error": f"{field} is required."}), 400
    result = user_service.create(data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201

@users_api_bp.route("/<int:item_id>", methods=["PUT"])
def update_user(item_id):
    """Update a user."""
    data = request.get_json()
    result = user_service.update(item_id, data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@users_api_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_user(item_id):
    """Delete a user."""
    result = user_service.delete(item_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

logger.info("User API routes instantiated successfully.")
