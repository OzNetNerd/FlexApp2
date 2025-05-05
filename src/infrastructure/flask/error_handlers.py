# src/infrastructure/flask/error_handlers.py

"""
Flask error handlers.

This module defines application-wide error handlers.
"""

from flask import request

from src.infrastructure.logging import get_logger
from src.infrastructure.flask.template_renderer import handle_template_error

logger = get_logger()


def register_error_handlers(app):
    """
    Register error handlers for the Flask application.

    Args:
        app: Flask application instance.
    """

    @app.errorhandler(TypeError)
    def handle_type_error(e):
        """
        Render a friendly error page when a TypeError occurs.

        Args:
            e: TypeError exception instance.

        Returns:
            Response: A rendered error template.
        """
        logger.error(f"TypeError: {e}")
        return handle_template_error(e, request.endpoint or "", request.path, "An error occurred while preparing the page context")
