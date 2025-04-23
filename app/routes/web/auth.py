# app/routes/auth.py

from flask import Blueprint
from app.routes.web.route_registration import register_auth_route
from app.services.auth import AuthService
from app.models.user import User

from app.utils.app_logging import get_logger

logger = get_logger()

# Define the blueprint
auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

# Create a service instance
auth_service = AuthService(User)

# Register routes using AuthService handlers
register_auth_route(auth_bp, "/login", auth_service.handle_login, "login", methods=["GET", "POST"])
register_auth_route(auth_bp, "/logout", auth_service.handle_logout, "logout", methods=["GET"])
