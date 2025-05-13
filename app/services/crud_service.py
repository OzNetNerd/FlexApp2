# app/routes/api/route_registration.py

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union

from flask import Blueprint, request
from flask.typing import ResponseReturnValue

from app.models.base import db
from app.routes.api.context import EntityApiContext, ErrorApiContext, ListApiContext
from app.routes.api.json_utils import json_endpoint
from app.utils.app_logging import get_logger
from app.services.service_base import CRUDService  # Import the CRUDService from service_base

logger = get_logger()


class CRUDEndpoint(Enum):
    GET_ALL = "get_all"
    GET_BY_ID = "get_by_id"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class ApiCrudRouteConfig:
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
    try:
        if endpoint == CRUDEndpoint.GET_ALL.value:
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 15, type=int)
            sort_column = request.args.get("sort_column", "id", type=str)
            sort_direction = request.args.get("sort_direction", "asc", type=str)
            filters = None
            if request.args.get("filters"):
                try:
                    filters = json.loads(request.args.get("filters"))
                except Exception as e:
                    logger.warning(f"Failed to parse filters parameter: {e}")
            result = service.get_all(page, per_page, sort_column, sort_direction, filters)
            if hasattr(result, "items"):
                return ListApiContext(entity_table_name=entity_table_name, items=result.items,
                                      total_count=getattr(result, "total", None))
            return ListApiContext(entity_table_name=entity_table_name, items=result)

        if endpoint == CRUDEndpoint.GET_BY_ID.value and entity_id is not None:
            entity = service.get_by_id(entity_id)
            if not entity:
                return ErrorApiContext(message=f"{entity_table_name} not found", status_code=404)
            return EntityApiContext(entity_table_name=entity_table_name, entity=entity)

        if endpoint == CRUDEndpoint.CREATE.value and data is not None:
            entity = service.create(data)
            return EntityApiContext(
                entity_table_name=entity_table_name,
                entity=entity,
                message=f"{entity_table_name} created successfully",
            )

        if endpoint == CRUDEndpoint.UPDATE.value and entity_id is not None and data is not None:
            existing = service.get_by_id(entity_id)
            if not existing:
                return ErrorApiContext(message=f"{entity_table_name} not found", status_code=404)
            entity = service.update(existing, data)
            return EntityApiContext(
                entity_table_name=entity_table_name,
                entity=entity,
                message=f"{entity_table_name} updated successfully",
            )

        if endpoint == CRUDEndpoint.DELETE.value and entity_id is not None:
            existing = service.get_by_id(entity_id)
            if not existing:
                return ErrorApiContext(message=f"{entity_table_name} not found", status_code=404)
            service.delete(entity_id)
            return {"message": f"{entity_table_name} deleted successfully"}

        return ErrorApiContext(message="Invalid operation or parameters", status_code=400)
    except Exception as e:
        logger.error(f"Error in API CRUD operation {endpoint!r}: {e}", exc_info=True)
        return ErrorApiContext(message="Internal server error", status_code=500)


def register_api_route(
        blueprint: Blueprint, url: str, handler: Callable[..., ResponseReturnValue], endpoint: str,
        methods: Optional[List[str]] = None
) -> None:
    blueprint.add_url_rule(rule=url, endpoint=endpoint, view_func=handler, methods=methods or ["GET"])


def make_func(action: str, svc: Any, entity: str) -> tuple[str, list[str], Callable]:
    if action == CRUDEndpoint.GET_ALL.value:
        def get_all():
            return handle_api_crud_operation(action, svc, entity)

        return "/", ["GET"], get_all

    if action == CRUDEndpoint.GET_BY_ID.value:
        def get_by_id(entity_id):
            return handle_api_crud_operation(action, svc, entity, entity_id)

        return "/<int:entity_id>", ["GET"], get_by_id

    if action == CRUDEndpoint.CREATE.value:
        def create():
            return handle_api_crud_operation(action, svc, entity, data=request.get_json())

        return "/", ["POST"], create

    if action == CRUDEndpoint.UPDATE.value:
        def update(entity_id):
            return handle_api_crud_operation(action, svc, entity, entity_id, data=request.get_json())

        return "/<int:entity_id>", ["PUT"], update

    if action == CRUDEndpoint.DELETE.value:
        def delete(entity_id):
            return handle_api_crud_operation(action, svc, entity, entity_id)

        return "/<int:entity_id>", ["DELETE"], delete

    return "", [], None


def register_api_crud_routes(config: ApiCrudRouteConfig) -> Blueprint:
    logger.info(f"Registering CRUD routes for {config.entity_table_name!r}")

    bp = config.blueprint
    entity = config.entity_table_name
    svc = config.service
    include = config.include_routes or [e.value for e in CRUDEndpoint]

    for action in include:
        if action not in [e.value for e in CRUDEndpoint]:
            continue

        url, methods, func = make_func(action, svc, entity)
        if func is None:
            continue

        handler = json_endpoint(func)
        handler.__name__ = action
        register_api_route(bp, url, handler, endpoint=action, methods=methods)
        logger.info(f"Registered API route {action!r} @ {url!r}")

    return bp


def create_crud_service(model: Type[db.Model], required_fields: Optional[List[str]] = None) -> CRUDService:
    """
    Factory function to create a CRUDService instance for a model.

    Args:
        model: The SQLAlchemy model class
        required_fields: Optional list of field names that are required when creating entities

    Returns:
        An instance of CRUDService for the model
    """
    return CRUDService(model_class=model, required_fields=required_fields)