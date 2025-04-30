# app/routes/web/route_registration.py - Improved debugging

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from flask import Blueprint, redirect, request, url_for
from flask_login import login_required

from app.routes.web.components.template_renderer import RenderSafelyConfig, render_safely
from app.routes.web.context import TableWebContext, WebContext
from app.utils.app_logging import get_logger

logger = get_logger()


class CRUDEndpoint(Enum):
    index = "index"
    create = "create"
    view = "view"
    edit = "edit"
    delete = "delete"

    @classmethod
    def is_valid(cls, name: str) -> bool:
        return name in cls._value2member_map_


@dataclass
class CrudRouteConfig:
    blueprint: Blueprint
    entity_table_name: str
    service: Any
    model_class: Any

    # Template paths with explicit initialization
    index_template: str = ""
    create_template: str = ""
    view_template: str = ""
    edit_template: str = ""

    def get_template(self, route_type: str, default: str) -> str:
        if route_type == "index":
            return self.index_template or default
        elif route_type == "create":
            return self.create_template or default
        elif route_type == "view":
            return self.view_template or default
        elif route_type == "edit":
            return self.edit_template or default
        return default


def route_handler(endpoint: str, config: CrudRouteConfig) -> Callable:
    def handler(*args, **kwargs):
        logger.info(f"Handling {request.method} {endpoint} with args={args}, kwargs={kwargs}")

        # Handle form submissions for create/edit/delete
        if request.method == "POST" and CRUDEndpoint.is_valid(endpoint):
            result = handle_crud_operation(
                endpoint,
                config.service,
                config.blueprint.name,
                kwargs.get("entity_id"),
                request.form.to_dict(),
            )
            if result:
                return result

        entity = None
        read_only = True

        # Determine if this is create or edit (non-read-only)
        if endpoint in (CRUDEndpoint.create.value, CRUDEndpoint.edit.value):
            read_only = False

        # Load existing entity for view/edit
        if endpoint in (CRUDEndpoint.view.value, CRUDEndpoint.edit.value):
            entity_id = kwargs.get("entity_id")
            entity = config.service.get_by_id(entity_id)
            logger.info(f"Loaded entity for {endpoint}: ID={entity_id}, entity={entity}")

        # Build appropriate context object
        if endpoint == CRUDEndpoint.index.value:
            context = TableWebContext(entity_table_name=config.entity_table_name)
        elif endpoint == CRUDEndpoint.create.value:
            # Initialize with default empty values for required fields
            default_entity = {"id": "", "question": "", "answer": "", "category": "", "last_reviewed": None, "due_date": None}

            context = TableWebContext(
                entity=default_entity,  # Use default entity instead of empty dict
                entity_table_name=config.entity_table_name,
                action="create",
                read_only=False,
                title=f"Create {config.entity_table_name}",
            )
        elif endpoint in (CRUDEndpoint.view.value, CRUDEndpoint.edit.value):
            entity_id = kwargs.get("entity_id")
            title = f"{'View' if endpoint == CRUDEndpoint.view.value else 'Edit'} {config.entity_table_name}"

            context = TableWebContext(
                entity=entity,
                entity_table_name=config.entity_table_name,
                action=endpoint,
                entity_id=entity_id,
                read_only=read_only,
                title=title,
            )

            # Add missing variables required by the template
            context.id = entity_id  # Template uses "id" but context has "entity_id"
            context.model_name = config.model_class.__name__  # Set model name from class

            # Get entity name for display
            if hasattr(entity, "name"):
                context.entity_name = entity.name
            elif hasattr(entity, "title"):
                context.entity_name = entity.title
            else:
                context.entity_name = f"{config.model_class.__name__} #{entity_id}"

            # Set submit_url even for read-only views (for proper form structure)
            if endpoint == CRUDEndpoint.view.value:
                context.submit_url = url_for(f"{config.blueprint.name}.update", entity_id=entity_id)
        else:
            context = WebContext(title=config.entity_table_name)

        # ---------------------------------------------------------------------
        # Generate CSRF token (if available)
        # ---------------------------------------------------------------------
        try:
            from flask_wtf.csrf import generate_csrf
            from markupsafe import Markup

            context.csrf_token = generate_csrf()
            context.csrf_input = Markup(f'<input type="hidden" name="csrf_token" value="{generate_csrf()}">')
        except ImportError:
            context.csrf_token = ""
            context.csrf_input = ""

        # Set submit URL for form actions
        if not read_only:
            if endpoint == CRUDEndpoint.create.value:
                context.submit_url = url_for(f"{config.blueprint.name}.create")
            elif endpoint == CRUDEndpoint.edit.value:
                context.submit_url = url_for(f"{config.blueprint.name}.update", entity_id=entity_id)

        # Render the template
        template_path = config.get_template(
            endpoint,
            f"pages/crud/{endpoint}_{config.entity_table_name.lower()}.html",
        )
        endpoint_name = f"{config.blueprint.name}.{endpoint}"

        logger.info(f"Rendering template: {template_path} with context: {type(context).__name__}")

        cfg = RenderSafelyConfig(
            template_path=template_path,
            context=context,
            error_message=f"Error rendering {config.entity_table_name} {endpoint}",
            endpoint_name=endpoint_name,
        )
        return render_safely(cfg)

    handler.__name__ = endpoint
    return login_required(handler)


def handle_crud_operation(endpoint: str, service: Any, blueprint_name: str, entity_id: Optional[int], form_data: Dict[str, Any]) -> Any:
    if endpoint == CRUDEndpoint.create.value:
        entity = service.create(form_data)
        return redirect(url_for(f"{blueprint_name}.view", entity_id=entity.id))
    if endpoint == CRUDEndpoint.edit.value:
        entity = service.update(service.get_by_id(entity_id), form_data)
        return redirect(url_for(f"{blueprint_name}.view", entity_id=entity.id))
    if endpoint == CRUDEndpoint.delete.value:
        service.delete(entity_id)
        return redirect(url_for(f"{blueprint_name}.index"))
    return None


def register_crud_routes(config: CrudRouteConfig) -> None:
    bp = config.blueprint
    bp.add_url_rule(rule="/", endpoint="index", view_func=route_handler("index", config), methods=["GET"])
    bp.add_url_rule(rule="/create", endpoint="create", view_func=route_handler("create", config), methods=["GET", "POST"])
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


def register_auth_route(blueprint: Blueprint, url: str, handler: Callable, endpoint_name: str, methods: Optional[List[str]] = None) -> None:
    methods = methods or ["GET"]
    blueprint.add_url_rule(rule=url, endpoint=endpoint_name, view_func=handler, methods=methods)
