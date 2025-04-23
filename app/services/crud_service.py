# app/routes/api/route_registration.py


import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union

from flask import Blueprint, request
from flask.typing import ResponseReturnValue

from app.models.base import db
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



class CRUDService:
    """Generic service for basic CRUD operations on a SQLAlchemy model."""

    def __init__(self, model: Type[db.Model], required_fields: Optional[List[str]] = None):
        self.model = model
        self.required_fields = required_fields or []

    def get_by_id(self, entity_id: int):
        return self.model.query.get(entity_id)

    def create(self, data: dict):
        self._validate_required_fields(data)
        entity = self.model(**data)
        db.session.add(entity)
        db.session.commit()
        return entity

    def update(self, entity, data: dict):
        for key, value in data.items():
            setattr(entity, key, value)
        db.session.commit()
        return entity

    def delete(self, entity_id: int):
        entity = self.get_by_id(entity_id)
        if entity:
            db.session.delete(entity)
            db.session.commit()

    def _validate_required_fields(self, data: dict):
        missing = [field for field in self.required_fields if field not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")


def handle_api_crud_operation(
        endpoint: str,
        service: Any,
        entity_table_name: str,
        entity_id: Optional[Union[int, str]] = None,
        data: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Handle CRUD operations based on endpoint type and return a Context object.
    """
    try:
        if endpoint == CRUDEndpoint.GET_ALL.value:
            # Extract pagination params from request
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 15, type=int)
            sort_column = request.args.get('sort_column', 'id', type=str)
            sort_direction = request.args.get('sort_direction', 'asc', type=str)

            # Extract filters if present
            filters = None
            if request.args.get('filters'):
                try:
                    filters = json.loads(request.args.get('filters'))
                except Exception as e:
                    logger.warning(f"Failed to parse filters parameter: {e}")

            result = service.get_all(page, per_page, sort_column, sort_direction, filters)
            if hasattr(result, "items"):
                return ListAPIContext(entity_table_name=entity_table_name, items=result.items,
                                      total_count=getattr(result, "total", None))
            return ListAPIContext(entity_table_name=entity_table_name, items=result)

        if endpoint == CRUDEndpoint.GET_BY_ID.value and entity_id is not None:
            entity = service.get_by_id(entity_id)
            if not entity:
                return ErrorAPIContext(message=f"{entity_table_name} not found", status_code=404)
            return EntityAPIContext(entity_table_name=entity_table_name, entity=entity)

        if endpoint == CRUDEndpoint.CREATE.value and data is not None:
            entity = service.create(data)
            return EntityAPIContext(
                entity_table_name=entity_table_name,
                entity=entity,
                message=f"{entity_table_name} created successfully",
            )

        if endpoint == CRUDEndpoint.UPDATE.value and entity_id is not None and data is not None:
            existing = service.get_by_id(entity_id)
            if not existing:
                return ErrorAPIContext(message=f"{entity_table_name} not found", status_code=404)
            entity = service.update(existing, data)
            return EntityAPIContext(
                entity_table_name=entity_table_name,
                entity=entity,
                message=f"{entity_table_name} updated successfully",
            )

        if endpoint == CRUDEndpoint.DELETE.value and entity_id is not None:
            existing = service.get_by_id(entity_id)
            if not existing:
                return ErrorAPIContext(message=f"{entity_table_name} not found", status_code=404)
            service.delete(entity_id)
            return {"message": f"{entity_table_name} deleted successfully"}

        return ErrorAPIContext(message="Invalid operation or parameters", status_code=400)
    except Exception as e:
        logger.error(f"Error in API CRUD operation '{endpoint}': {e}", exc_info=True)
        return ErrorAPIContext(message="Internal server error", status_code=500)


def register_api_route(
        blueprint: Blueprint, url: str, handler: Callable[..., ResponseReturnValue], endpoint: str,
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

    for action in include:
        if action not in [e.value for e in CRUDEndpoint]:
            continue

        # Define URL and HTTP methods
        if action == CRUDEndpoint.GET_ALL.value:
            url = "/"
            methods = ["GET"]
            func = lambda: handle_api_crud_operation(action, svc, entity)
        elif action == CRUDEndpoint.GET_BY_ID.value:
            url = "/<int:entity_id>"
            methods = ["GET"]
            func = lambda entity_id: handle_api_crud_operation(action, svc, entity, entity_id)
        elif action == CRUDEndpoint.CREATE.value:
            url = "/"
            methods = ["POST"]
            func = lambda: handle_api_crud_operation(action, svc, entity, data=request.get_json())
        elif action == CRUDEndpoint.UPDATE.value:
            url = "/<int:entity_id>"
            methods = ["PUT"]
            func = lambda entity_id: handle_api_crud_operation(action, svc, entity, entity_id, data=request.get_json())
        elif action == CRUDEndpoint.DELETE.value:
            url = "/<int:entity_id>"
            methods = ["DELETE"]
            func = lambda entity_id: handle_api_crud_operation(action, svc, entity, entity_id)
        else:
            continue

        # Wrap the handler with json_endpoint
        handler = json_endpoint(func)
        handler.__name__ = action

        # Register the route
        register_api_route(bp, url, handler, endpoint=action, methods=methods)
        logger.info(f"Registered API route {action} @ {url}")

    return bp