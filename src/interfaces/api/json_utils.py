"""Utilities for handling JSON in API routes.

This module provides utilities for converting API responses to JSON,
with special handling for different context types.
"""

import functools
from typing import Any, Callable, Dict, Union

from flask import jsonify, Response
from flask.typing import ResponseReturnValue

from interfaces.api.context import EntityApiContext, ErrorApiContext, ListApiContext


def serialize_context(context: Any) -> Dict[str, Any]:
    """Serialize API context objects to dictionary for JSON response.

    Args:
        context: The context object to serialize.

    Returns:
        A dictionary representation of the context.
    """
    if isinstance(context, EntityApiContext):
        response = {
            "data": context.entity,
            "type": context.entity_table_name,
        }
        if context.message:
            response["message"] = context.message
        return response

    if isinstance(context, ListApiContext):
        response = {
            "data": context.items,
            "type": context.entity_table_name,
        }
        if context.total_count is not None:
            response["total"] = context.total_count
        return response

    if isinstance(context, ErrorApiContext):
        response = {
            "error": {
                "message": context.message,
                "code": context.status_code,
            }
        }
        if context.details:
            response["error"]["details"] = context.details
        return response

    # If it's already a dict, return it
    if isinstance(context, dict):
        return context

    # Try to convert to dict if it has __dict__
    if hasattr(context, "__dict__"):
        return context.__dict__

    # Last resort: try to serialize the object
    return {"data": str(context)}


def json_endpoint(func: Callable[..., Any]) -> Callable[..., ResponseReturnValue]:
    """Decorator to convert function return values to JSON responses.

    Args:
        func: The view function to decorate.

    Returns:
        The decorated function that returns Flask JSON responses.

    Example:
        ```python
        @app.route('/api/users')
        @json_endpoint
        def get_users():
            users = user_service.get_all()
            return ListApiContext(entity_table_name="user", items=users)
        ```
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Union[Response, ResponseReturnValue]:
        result = func(*args, **kwargs)
        if isinstance(result, ErrorApiContext):
            return jsonify(serialize_context(result)), result.status_code
        return jsonify(serialize_context(result))

    return wrapper