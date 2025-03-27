import logging
from flask import request

logger = logging.getLogger(__name__)


class RequestLogger:
    """Handles logging of HTTP request information."""

    def log_request_info(self, model_name: str, route_name: str, item_id: int = None) -> None:
        """
        Log detailed HTTP request information for debugging purposes.

        Args:
            model_name (str): The name of the model being accessed.
            route_name (str): The route or endpoint name.
            item_id (int, optional): The ID of the item, if available.
        """
        item_info = f" with id {item_id}" if item_id else ""
        logger.debug(f"Request to {route_name} route for {model_name}{item_info}")
        logger.debug(f"Path: {request.path} | Method: {request.method} | Args: {dict(request.args)}")
        logger.debug(f"Headers: {dict(request.headers)}")
