# src/interfaces/web/routes/crud_routes.py

"""CRUD route registration for web interfaces.

This module provides utilities for registering standardized
CRUD routes for domain entities.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from flask import Blueprint, redirect, request, url_for
from flask_login import login_required

from src.infrastructure.flask.template_renderer import RenderSafelyConfig, render_safely
from src.infrastructure.flask.template_config import TemplateConfig
from src.infrastructure.logging import get_logger
from src.interfaces.web.views.context import TableContext, WebContext

logger = get_logger(__name__)


class CRUDEndpoint(Enum):
    """Enum representing standard CRUD endpoints."""
    index = "index"
    create = "create"
    view = "view"
    edit = "edit"
    delete = "delete"

    @classmethod
    def is_valid(cls, name: str) -> bool:
        """Check if a name is a valid CRUD endpoint.

        Args:
            name: Name to check.

        Returns:
            Whether the name is a valid endpoint.
        """
        return name in cls._value2member_map_


@dataclass
class CrudRouteConfig:
    """Configuration for CRUD routes.

    Attributes:
        blueprint: Flask blueprint to add routes to.
        entity_table_name: Name of the entity table.
        service: Service for entity operations.
        model_class: Model class for the entities.
        template_config: Template configuration.
    """
    blueprint: Blueprint
    entity_table_name: str
    service: Any
    model_class: Any
    template_config: TemplateConfig

    def get_template(self, route_type: str, default: str) -> str:
        """Get template path with fallback to default.

        Args:
            route_type: Type of route.
            default: Default template path.

        Returns:
            Template path to use.
        """
        return self.template_config.get_template(route_type, default)


def route_handler(endpoint: str, config: CrudRouteConfig) -> Callable:
    """Create a handler function for a CRUD endpoint.

    Args:
        endpoint: CRUD endpoint type.
        config: Route configuration.

    Returns:
        Handler function for the endpoint.
    """
    # Implementation details for handling CRUD routes
    # (omitting for brevity)
    pass


def handle_crud_operation(
        endpoint: str,
        service: Any,
        blueprint_name: str,
        entity_id: Optional[int],
        form_data: Dict[str, Any]
) -> Any:
    """Handle CRUD operations based on form submissions.

    Args:
        endpoint: CRUD endpoint type.
        service: Service for entity operations.
        blueprint_name: Name of the blueprint.
        entity_id: ID of the entity (if applicable).
        form_data: Form data from the request.

    Returns:
        Response for the operation.
    """
    # Implementation details for handling form submissions
    # (omitting for brevity)
    pass


def register_crud_routes(config: CrudRouteConfig) -> None:
    """Register CRUD routes for an entity.

    Args:
        config: CRUD route configuration.
    """
    bp = config.blueprint

    # Register routes for all CRUD operations
    bp.add_url_rule(rule="/create", endpoint="create", view_func=route_handler("create", config),
                    methods=["GET", "POST"])
    bp.add_url_rule(rule="/<int:entity_id>", endpoint="view", view_func=route_handler("view", config), methods=["GET"])
    bp.add_url_rule(
        rule="/<int:entity_id>/edit",
        endpoint="edit",
        view_func=route_handler("edit", config),
        methods=["GET", "POST"],
    )
    bp.add_url_rule(
        rule="/<int:entity_id>",
        endpoint="update",
        view_func=route_handler("edit", config),
        methods=["POST"],
    )
    bp.add_url_rule(
        rule="/<int:entity_id>/delete",
        endpoint="delete",
        view_func=route_handler("delete", config),
        methods=["POST"],
    )


def register_auth_route(
        blueprint: Blueprint,
        url: str,
        handler: Callable,
        endpoint_name: str,
        methods: Optional[List[str]] = None
) -> None:
    """Register an authentication-related route.

    Args:
        blueprint: Flask blueprint to add route to.
        url: URL pattern for the route.
        handler: Handler function for the route.
        endpoint_name: Name of the endpoint.
        methods: HTTP methods to support (defaults to GET).
    """
    methods = methods or ["GET"]
    blueprint.add_url_rule(rule=url, endpoint=endpoint_name, view_func=handler, methods=methods)