# api/route_registration.py

import logging
from typing import Callable, List, Optional, Any, Dict, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from flask import Blueprint, request, jsonify

from app.utils.table_helpers import get_table_plural_name
from app.routes.api.context import ListAPIContext, EntityAPIContext, ErrorAPIContext

logger = logging.getLogger(__name__)


class CRUDEndpoint(Enum):
    GET_ALL = "get_all"
    GET_BY_ID = "get_by_id"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

    @classmethod
    def is_valid(cls, endpoint: str) -> bool:
        return any(endpoint == item.value for item in cls)


@dataclass
class ApiCrudRouteConfig:
    """Configuration for API CRUD routes."""
    blueprint: Blueprint
    entity_table_name: str
    service: Any
    include_routes: Optional[List[str]] = None


def json_response(context: Any, status_code: int = 200) -> Tuple[Any, int]:
    """Convert a context object to a JSON response with proper status code."""
    if hasattr(context, 'to_dict'):
        data = context.to_dict()
    elif isinstance(context, dict):
        data = context
    else:
        data = {"data": str(context)}

    # If it's an error context, use its status code
    if hasattr(context, 'status_code'):
        status_code = context.status_code

    return jsonify(data), status_code


def handle_api_crud_operation(
        endpoint: str,
        service: Any,
        entity_table_name: str,
        entity_id: Optional[Union[str, int]] = None,
        data: Optional[Dict[str, Any]] = None
) -> Any:
    """Handle CRUD operations based on endpoint type."""
    if not service:
        logger.error(f"No service available for {endpoint}")
        return ErrorAPIContext(
            message="Service not available for this operation",
            status_code=500
        )

    try:
        if endpoint == CRUDEndpoint.GET_ALL.value:
            query_result = service.get_all()

            # Handle pagination objects by extracting items and total_count
            if hasattr(query_result, 'items'):
                items = query_result.items
                total_count = getattr(query_result, 'total_count', None)
            else:
                items = query_result
                total_count = None

            # Create the context with extracted items
            return ListAPIContext(
                entity_table_name=entity_table_name,
                items=items,
                total_count=total_count
            )

        elif endpoint == CRUDEndpoint.GET_BY_ID.value and entity_id:
            entity = service.get_by_id(entity_id)
            if not entity:
                return ErrorAPIContext(
                    message=f"{entity_table_name} not found",
                    status_code=404
                )
            return EntityAPIContext(entity_table_name=entity_table_name, entity=entity)

        elif endpoint == CRUDEndpoint.CREATE.value and data:
            result = service.create(data)
            if isinstance(result, dict) and result.get("error"):
                return ErrorAPIContext(
                    message=result.get("error"),
                    status_code=400
                )
            return EntityAPIContext(
                entity_table_name=entity_table_name,
                entity=result,
                message=f"{entity_table_name} created successfully"
            )

        elif endpoint == CRUDEndpoint.UPDATE.value and entity_id and data:
            entity = service.get_by_id(entity_id)
            if not entity:
                return ErrorAPIContext(
                    message=f"{entity_table_name} not found",
                    status_code=404
                )

            result = service.update(entity, data)
            if isinstance(result, dict) and result.get("error"):
                return ErrorAPIContext(
                    message=result.get("error"),
                    status_code=400
                )
            return EntityAPIContext(
                entity_table_name=entity_table_name,
                entity=result,
                message=f"{entity_table_name} updated successfully"
            )

        elif endpoint == CRUDEndpoint.DELETE.value and entity_id:
            entity = service.get_by_id(entity_id)
            if not entity:
                return ErrorAPIContext(
                    message=f"{entity_table_name} not found",
                    status_code=404
                )

            result = service.delete(entity_id)
            if isinstance(result, dict) and result.get("error"):
                return ErrorAPIContext(
                    message=result.get("error"),
                    status_code=400
                )
            return {"message": f"{entity_table_name} deleted successfully"}

    except Exception as e:
        logger.error(f"Error in API operation: {e}", exc_info=True)
        return ErrorAPIContext(
            message=f"Error processing request: {str(e)}",
            status_code=500
        )

    return ErrorAPIContext(
        message="Invalid operation or missing required parameters",
        status_code=400
    )


def register_api_route(
        blueprint: Blueprint,
        url: str,
        handler: Callable,
        endpoint: str,
        methods: Optional[List[str]] = None
) -> Blueprint:
    """Register an API route with the given blueprint."""
    if methods is None:
        methods = ["GET"]

    logger.info(f"Registering API route '{endpoint}' at '{url}' with methods {methods}")
    blueprint.add_url_rule(url, endpoint=endpoint, view_func=handler, methods=methods)
    logger.info(f"Registered API route '{endpoint}' at '{url}'")

    return blueprint


def register_api_crud_routes(config: ApiCrudRouteConfig) -> Blueprint:
    """Register CRUD API routes based on configuration."""
    logger.info("Starting registration of API CRUD routes.")

    blueprint = config.blueprint
    entity_table_name = config.entity_table_name
    service = config.service

    if not isinstance(entity_table_name, str):
        logger.error("Invalid entity_table_name type; expected a string.")
        raise ValueError("The 'entity_table_name' must be a string.")

    logger.info(f"Entity table name is valid: {entity_table_name}")

    include_routes = config.include_routes or [
        "get_all", "get_by_id", "create", "update", "delete"
    ]

    logger.info(f"Routes to include: {include_routes}")

    entity_table_plural_name = get_table_plural_name(entity_table_name)
    logger.info(f"Plural name for the entity table '{entity_table_name}': {entity_table_plural_name}")

    # Configure all route handlers
    route_configs = {
        "get_all": {
            "url": "/",
            "methods": ["GET"],
            "handler": lambda: json_response(
                handle_api_crud_operation(
                    CRUDEndpoint.GET_ALL.value,
                    service,
                    entity_table_name
                )
            )
        },
        "get_by_id": {
            "url": "/<int:entity_id>",
            "methods": ["GET"],
            "handler": lambda entity_id: json_response(
                handle_api_crud_operation(
                    CRUDEndpoint.GET_BY_ID.value,
                    service,
                    entity_table_name,
                    entity_id
                )
            )
        },
        "create": {
            "url": "/",
            "methods": ["POST"],
            "handler": lambda: json_response(
                handle_api_crud_operation(
                    CRUDEndpoint.CREATE.value,
                    service,
                    entity_table_name,
                    data=request.get_json()
                ),
                201
            )
        },
        "update": {
            "url": "/<int:entity_id>",
            "methods": ["PUT"],
            "handler": lambda entity_id: json_response(
                handle_api_crud_operation(
                    CRUDEndpoint.UPDATE.value,
                    service,
                    entity_table_name,
                    entity_id,
                    data=request.get_json()
                )
            )
        },
        "delete": {
            "url": "/<int:entity_id>",
            "methods": ["DELETE"],
            "handler": lambda entity_id: json_response(
                handle_api_crud_operation(
                    CRUDEndpoint.DELETE.value,
                    service,
                    entity_table_name,
                    entity_id
                )
            )
        },
    }

    # Register routes based on configuration
    for route_type in [r for r in include_routes if r in route_configs]:
        config = route_configs[route_type]
        logger.info(f"Processing registration for API route type: '{route_type}'")

        # Create a route handler with proper closure
        def create_handler(handler_func):
            def wrapped_handler(*args, **kwargs):
                try:
                    return handler_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in API handler: {e}", exc_info=True)
                    return json_response(
                        ErrorAPIContext(
                            message=f"Internal server error: {str(e)}",
                            status_code=500
                        )
                    )

            # Ensure the handler has the correct name for Flask
            wrapped_handler.__name__ = route_type
            return wrapped_handler

        register_api_route(
            blueprint=blueprint,
            url=config["url"],
            handler=create_handler(config["handler"]),
            endpoint=route_type,
            methods=config["methods"],
        )

        logger.info(f"Successfully registered API route '{route_type}'.")

    logger.info("API CRUD route registration completed successfully.")
    return blueprint