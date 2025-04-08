# app/routes/auth.py

import logging
from flask import Blueprint
from app.routes.base.web_utils import register_auth_route
from app.services.auth import AuthService
from app.models.user import User

logger = logging.getLogger(__name__)

# Define the blueprint
auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

# Create a service instance
auth_service = AuthService(User)

# Register routes using AuthService handlers
register_auth_route(auth_bp, "/login", auth_service.handle_login, "login", methods=["GET", "POST"])
register_auth_route(auth_bp, "/logout", auth_service.handle_logout, "logout", methods=["GET"])
