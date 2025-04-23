from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from flask import Blueprint, request
from flask.typing import ResponseReturnValue

from app.routes.api.context import EntityAPIContext, ErrorAPIContext, ListAPIContext
from app.routes.api.json_utils import json_endpoint
from app.utils.app_logging import get_logger

logger = get_logger()


class CRUDEndpoint(Enum):
    GET_ALL = "get_all"
    GET_BY_ID = "get_by_id"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class ApiCrudRouteConfig:
    """Configuration for API CRUD routes."""
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
    """Handle CRUD operations based on endpoint type and return a Context object."""
    try:
        if endpoint == CRUDEndpoint.GET_ALL.value:
            result = service.get_all()
            if hasattr(result, "items"):
                return ListAPIContext(entity_table_name=entity_table_name, items=result.items, total_count=getattr(result, "total", None))
            return ListAPIContext(entity_table_name=entity_table_name, items=result)

        if endpoint == CRUDEndpoint.GET_BY_ID.value and entity_id is not None:
            entity = service.get_by_id(entity_id)
            if not entity:
                return ErrorAPIContext(message=f"{entity_table_name} not found", status_code=404)
            return EntityAPIContext(entity_table_name=entity_table_name, entity=entity)

        if endpoint == CRUDEndpoint.CREATE.value and data is not None:
            entity = service.create(data)
            return EntityAPIContext(entity_table_name=entity_table_name, entity=entity, message=f"{entity_table_name} created successfully")

        if endpoint == CRUDEndpoint.UPDATE.value and entity_id is not None and data is not None:
            existing = service.get_by_id(entity_id)
            if not existing:
                return ErrorAPIContext(message=f"{entity_table_name} not found", status_code=404)
            entity = service.update(existing, data)
            return EntityAPIContext(entity_table_name=entity_table_name, entity=entity, message=f"{entity_table_name} updated successfully")

        if endpoint == CRUDEndpoint.DELETE.value and entity_id is not None:
            existing = service.get_by_id(entity_id)
            if not existing:
                return ErrorAPIContext(message=f"{entity_table_name} not found", status_code=404)
            service.delete(entity_id)
            return {"message": f"{entity_table_name} deleted successfully"}

        return ErrorAPIContext(message="Invalid operation or parameters", status_code=400)
    except Exception as e:
        logger.error(f"Error in API CRUD operation {endpoint!r}: {e}", exc_info=True)
        return ErrorAPIContext(message="Internal server error", status_code=500)


def register_api_route(
    blueprint: Blueprint,
    url: str,
    handler: Callable[..., ResponseReturnValue],
    endpoint: str,
    methods: Optional[List[str]] = None
) -> None:
    """Register a single route on an API blueprint."""
    blueprint.add_url_rule(rule=url, endpoint=endpoint, view_func=handler, methods=methods or ["GET"])


def register_api_crud_routes(config: ApiCrudRouteConfig) -> Blueprint:
    """Register CRUD API routes based on configuration, all wrapped with @json_endpoint."""
    logger.info(f"Registering CRUD routes for {config.entity_table_name}")

    bp = config.blueprint
    entity = config.entity_table_name
    svc = config.service
    include = config.include_routes or [e.value for e in CRUDEndpoint]

    def make_func(action: str):
        if action == CRUDEndpoint.GET_ALL.value:
            def func_get_all():
                return handle_api_crud_operation(action, svc, entity)
            return "/", ["GET"], func_get_all

        if action == CRUDEndpoint.GET_BY_ID.value:
            def func_get_by_id(entity_id):
                return handle_api_crud_operation(action, svc, entity, entity_id)
            return "/<int:entity_id>", ["GET"], func_get_by_id

        if action == CRUDEndpoint.CREATE.value:
            def func_create():
                return handle_api_crud_operation(action, svc, entity, data=request.get_json())
            return "/", ["POST"], func_create

        if action == CRUDEndpoint.UPDATE.value:
            def func_update(entity_id):
                return handle_api_crud_operation(action, svc, entity, entity_id, data=request.get_json())
            return "/<int:entity_id>", ["PUT"], func_update

        if action == CRUDEndpoint.DELETE.value:
            def func_delete(entity_id):
                return handle_api_crud_operation(action, svc, entity, entity_id)
            return "/<int:entity_id>", ["DELETE"], func_delete

        return None, None, None

    for action in include:
        if action not in [e.value for e in CRUDEndpoint]:
            continue

        url, methods, func = make_func(action)
        if not func:
            continue

        handler = json_endpoint(func)
        handler.__name__ = action
        register_api_route(bp, url, handler, endpoint=action, methods=methods)
        logger.info(f"Registered API route {action!r} @ {url!r}")

    return bp
