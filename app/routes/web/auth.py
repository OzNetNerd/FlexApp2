# app/routes/auth.py

import logging
from flask import Blueprint
from app.routes.base.web_utils import register_blueprint_routes
from app.services.auth import AuthService
from app.models.user import User

logger = logging.getLogger(__name__)

# Define the blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Create a service instance
auth_service = AuthService(User)

# Register auth routes - make sure route names match what's in the template
register_blueprint_routes(auth_bp, "Auth", routes=['login', 'logout'], service=auth_service)