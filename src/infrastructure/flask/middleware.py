# src/infrastructure/flask/middleware.py

"""
Flask middleware configuration.

This module defines request/response middleware for the Flask application.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from flask import current_app, redirect, request, url_for
from flask_login import current_user

from src.infrastructure.logging import get_logger

logger = get_logger()


def register_middleware(app):
    """
    Register Flask middleware functions.

    Args:
        app: Flask application instance.
    """

    @app.before_request
    def require_login():
        """
        Enforce authentication for non-whitelisted routes.

        Redirects unauthenticated users to the login page except for
        explicitly whitelisted routes like login, static assets, and API endpoints.
        """
        endpoint = request.endpoint or ""
        authenticated = current_user.is_authenticated

        # Log request if enabled
        if current_app.config["LOG_HTTP_REQUESTS"]:
            logger.info(f"require_login: endpoint={endpoint}, authenticated={authenticated}")

        # Check whitelist
        whitelisted = {"auth_bp.login", "auth_bp.logout", "static", "debug_session"}
        if not authenticated:
            # Allow access to whitelisted endpoints, static assets, API endpoints
            if endpoint in whitelisted or endpoint.startswith("static") or endpoint.startswith("api_") or endpoint.endswith(".data"):
                return None
            return redirect(url_for("auth_bp.login", next=request.path))

    @app.before_request
    def log_request():
        """Log HTTP request information if request logging is enabled."""
        if not current_app.config["LOG_HTTP_REQUESTS"]:
            return

        # Skip static asset requests
        if request.endpoint == "static":
            return

        request_id = getattr(request, "id", hex(id(request))[2:])
        logger.info(f"[{request_id}] {request.method} {request.path} from {request.remote_addr}")
