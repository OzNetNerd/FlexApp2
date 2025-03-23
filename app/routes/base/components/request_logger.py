import logging
from flask import request

logger = logging.getLogger(__name__)


class RequestLogger:
    """Handles logging of HTTP request information."""

    def log_request_info(self, model_name, route_name, item_id=None):
        """Log detailed request information."""
        item_info = f" with id {item_id}" if item_id else ""
        logger.debug(f"Request to {route_name} route for {model_name}{item_info}")
        logger.debug(
            f"Path: {request.path} | Method: {request.method} | Args: {dict(request.args)}"
        )
        logger.debug(f"Headers: {dict(request.headers)}")
