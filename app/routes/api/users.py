# api/users.py

import logging
from flask import Blueprint
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig
from app.models import User
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

# Create API blueprint
users_api_bp = Blueprint("api_users", __name__, url_prefix="/api/users")

# Create a service instance
user_service = UserService(User)

# Register all standard CRUD API routes
user_api_crud_config = ApiCrudRouteConfig(
    blueprint=users_api_bp,
    entity_table_name="User",
    service=user_service
)
register_api_crud_routes(user_api_crud_config)

# If you need custom routes beyond CRUD, you can add them here
# Example of a custom route:
# @users_api_bp.route("/search", methods=["GET"])
# def search_users():
#     query = request.args.get("q", "")
#     results = user_service.search(query)
#     return jsonify([user.to_dict() for user in results])

logger.info("User API routes registered successfully.")