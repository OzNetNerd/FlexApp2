# src/interfaces/api/crud_routes.py

"""Utilities for registering CRUD API routes.

This module provides tools for automatically registering standard CRUD
API routes with a Flask blueprint, reducing boilerplate code.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from flask import Blueprint, request
from flask.typing import ResponseReturnValue

from infrastructure.logging import get_logger
from interfaces.api.context import EntityApiContext, ErrorApiContext, ListApiContext
from interfaces.api.json_utils import json_endpoint

logger = get_logger()


class CRUDEndpoint(Enum):
    """Enum defining standard CRUD operations for API endpoints."""

    GET_ALL = "get_all"
    GET_BY_ID = "get_by_id"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class ApiCrudRouteConfig:
    """Configuration for API CRUD routes.

    Attributes:
        blueprint: Flask blueprint to register routes on.
        entity_table_name: Name of the entity's table.
        service: Service object that handles the CRUD operations.
        include_routes: Optional list of route types to include (defaults to all).
    """

    blueprint: Blueprint
    entity_table_name: str
    service: Any
    include_routes: Optional[List[str]] = None


def handle_api_crud_operation(
        endpoint: str,
        service: Any,
        entity_table_name: str,
        entity_id: Optional[Union[int, str]] = None,
        data: Optional[Dict[str, Any]] = None,
) -> Any:
    """Handle CRUD operations and return appropriate context objects.

    Args:
        endpoint: The type of CRUD operation (from CRUDEndpoint).
        service: The service object that implements CRUD methods.
        entity_table_name: Name of the entity's table.
        entity_id: Optional ID for entity-specific operations.
        data: Optional data for create/update operations.

    Returns:
        An appropriate context object or error.

    Raises:
        Exception: Any exceptions from the service are caught and returned as errors.
    """
    try:
        # GET_ALL operation
        if endpoint == CRUDEndpoint.GET_ALL.value:
            result = service.get_all()
            if hasattr(result, "items"):
                return ListApiContext(
                    entity_table_name=entity_table_name,
                    items=result.items,
                    total_count=getattr(result, "total", None)
                )
            return ListApiContext(
                entity_table_name=entity_table_name,
                items=result
            )

        # GET_BY_ID operation
        if endpoint == CRUDEndpoint.GET_BY_ID.value and entity_id is not None:
            entity = service.get_by_id(entity_id)
            if not entity:
                return ErrorApiContext(
                    message=f"{entity_table_name} not found",
                    status_code=404
                )
            return EntityApiContext(
                entity_table_name=entity_table_name,
                entity=entity
            )

        # CREATE operation
        if endpoint == CRUDEndpoint.CREATE.value and data is not None:
            entity = service.create(data)
            return EntityApiContext(
                entity_table_name=entity_table_name,
                entity=entity,
                message=f"{entity_table_name} created successfully"
            )

        # UPDATE operation
        if endpoint == CRUDEndpoint.UPDATE.value and entity_id is not None and data is not None:
            existing = service.get_by_id(entity_id)
            if not existing:
                return ErrorApiContext(
                    message=f"{entity_table_name} not found",
                    status_code=404
                )
            entity = service.update(existing, data)
            return EntityApiContext(
                entity_table_name=entity_table_name,
                entity=entity,
                message=f"{entity_table_name} updated successfully"
            )

        # DELETE operation
        if endpoint == CRUDEndpoint.DELETE.value and entity_id is not None:
            existing = service.get_by_id(entity_id)
            if not existing:
                return ErrorApiContext(
                    message=f"{entity_table_name} not found",
                    status_code=404
                )
            service.delete(entity_id)
            return {"message": f"{entity_table_name} deleted successfully"}

        # Invalid operation
        return ErrorApiContext(
            message="Invalid operation or parameters",
            status_code=400
        )
    except Exception as e:
        logger.error(f"Error in API CRUD operation {endpoint!r}: {e}", exc_info=True)
        return ErrorApiContext(
            message="Internal server error",
            status_code=500
        )


def register_api_route(
        blueprint: Blueprint,
        url: str,
        handler: Callable[..., ResponseReturnValue],
        endpoint: str,
        methods: Optional[List[str]] = None
) -> None:
    """Register a single route on an API blueprint.

    Args:
        blueprint: Flask blueprint to register the route on.
        url: URL path for the route.
        handler: View function that handles the route.
        endpoint: Endpoint name for the route.
        methods: HTTP methods allowed for the route.
    """
    blueprint.add_url_rule(
        rule=url,
        endpoint=endpoint,
        view_func=handler,
        methods=methods or ["GET"]
    )


def create_crud_handler(
        action: str,
        service: Any,
        entity_name: str
) -> Tuple[str, List[str], Callable[..., Any]]:
    """Create a handler function for a specific CRUD action.

    Args:
        action: The CRUD action type (from CRUDEndpoint).
        service: The service that implements CRUD methods.
        entity_name: Name of the entity.

    Returns:
        A tuple of (url, methods, handler_function).
    """
    if action == CRUDEndpoint.GET_ALL.value:
        def handler():
            return handle_api_crud_operation(action, service, entity_name)

        return "/", ["GET"], handler

    if action == CRUDEndpoint.GET_BY_ID.value:
        def handler(entity_id):
            return handle_api_crud_operation(action, service, entity_name, entity_id)

        return "/<int:entity_id>", ["GET"], handler

    if action == CRUDEndpoint.CREATE.value:
        def handler():
            return handle_api_crud_operation(action, service, entity_name, data=request.get_json())

        return "/", ["POST"], handler

    if action == CRUDEndpoint.UPDATE.value:
        def handler(entity_id):
            return handle_api_crud_operation(action, service, entity_name, entity_id, data=request.get_json())

        return "/<int:entity_id>", ["PUT"], handler

    if action == CRUDEndpoint.DELETE.value:
        def handler(entity_id):
            return handle_api_crud_operation(action, service, entity_name, entity_id)

        return "/<int:entity_id>", ["DELETE"], handler

    return None, None, None


def register_api_crud_routes(config: ApiCrudRouteConfig) -> Blueprint:
    """Register CRUD API routes based on configuration.

    All route handlers are wrapped with @json_endpoint to convert
    their return values to JSON responses.

    Args:
        config: Configuration for the CRUD routes.

    Returns:
        The blueprint with registered routes.

    Example:
        ```python
        bp = Blueprint("companies", __name__)
        register_api_crud_routes(ApiCrudRouteConfig(
            blueprint=bp,
            entity_table_name="company",
            service=company_service
        ))
        ```
    """
    logger.info(f"Registering CRUD routes for {config.entity_table_name}")

    bp = config.blueprint
    entity = config.entity_table_name
    service = config.service
    include = config.include_routes or [e.value for e in CRUDEndpoint]

    # Register each enabled CRUD route
    for action in include:
        if action not in [e.value for e in CRUDEndpoint]:
            continue

        url, methods, handler = create_crud_handler(action, service, entity)
        if not handler:
            continue

        # Wrap the handler with json_endpoint and register it
        json_handler = json_endpoint(handler)
        json_handler.__name__ = action
        register_api_route(bp, url, json_handler, endpoint=action, methods=methods)
        logger.info(f"Registered API route {action!r} @ {url!r}")

    return bp