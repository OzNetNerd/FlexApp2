from typing import Any, Callable, Optional, Dict, List
from flask import Blueprint, request, redirect, url_for
from dataclasses import dataclass
from enum import Enum

from app.utils.app_logging import get_logger
from app.utils.table_helpers import get_table_plural_name
from app.routes.web.components.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.context import TableContext, EntityContext, SimpleContext



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
class CrudTemplates:
    index: Optional[str] = None
    create: Optional[str] = None
    view: Optional[str] = None
    edit: Optional[str] = None

    def get(self, route_type: str, default: str) -> str:
        return getattr(self, route_type) or default

@dataclass
class CrudRouteConfig:
    blueprint: Blueprint
    entity_table_name: str
    service: Any
    templates: CrudTemplates


def default_crud_templates(entity_table_name: str) -> CrudTemplates:
    """
    Return default CRUD templates following a uniform structure:
      - pages/<plural>/index.html
      - pages/<plural>/create.html
      - pages/<plural>/view.html
      - pages/<plural>/edit.html
    """
    # Derive the lowercase plural form (e.g. "contacts" for "Contact")
    plural = get_table_plural_name(entity_table_name).lower()

    return CrudTemplates(
        index  = f"pages/{plural}/index.html",
        create = f"pages/{plural}/create.html",
        view   = f"pages/{plural}/view.html",
        edit   = f"pages/{plural}/edit.html",
    )

def route_handler(endpoint: str, config: CrudRouteConfig) -> Callable:
    def handler(*args, **kwargs):
        logger.info(f"Handling {request.method} {endpoint} with args={args}, kwargs={kwargs}")

        # POST operations
        if request.method == 'POST' and CRUDEndpoint.is_valid(endpoint):
            result = handle_crud_operation(
                endpoint,
                config.service,
                config.blueprint.name,
                kwargs.get('entity_id'),
                request.form.to_dict()
            )
            if result:
                return result

        # GET operations: build appropriate context
        if endpoint == CRUDEndpoint.index.value:
            context = TableContext(entity_table_name=config.entity_table_name)
        elif endpoint == CRUDEndpoint.create.value:
            context = EntityContext(entity=None, entity_table_name=config.entity_table_name, action='create')
        elif endpoint in (CRUDEndpoint.view.value, CRUDEndpoint.edit.value):
            entity_id = kwargs.get('entity_id')
            entity = config.service.get_by_id(entity_id)
            context = EntityContext(
                entity=entity,
                entity_table_name=config.entity_table_name,
                action=endpoint,
                entity_id=entity_id
            )
        else:
            context = SimpleContext(title=config.entity_table_name)

        # --- CSRF injection for all form-based views ---
        try:
            from flask_wtf.csrf import generate_csrf
            from markupsafe import Markup
            context.csrf_input = Markup(
                f'<input type="hidden" name="csrf_token" value="{generate_csrf()}">'
            )
        except ImportError:
            context.csrf_input = ''

        # Select the template
        template_path = config.templates.get(
            endpoint,
            f"pages/crud/{endpoint}_{config.entity_table_name.lower()}.html"
        )
        endpoint_name = f"{config.blueprint.name}.{endpoint}"

        cfg = RenderSafelyConfig(
            template_path=template_path,
            context=context,
            error_message=f"Error rendering {config.entity_table_name} {endpoint}",
            endpoint_name=endpoint_name
        )
        return render_safely(cfg)

    handler.__name__ = endpoint
    return handler



def handle_crud_operation(
    endpoint: str,
    service: Any,
    blueprint_name: str,
    entity_id: Optional[int],
    form_data: Dict[str, Any]
) -> Any:
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
    # Index
    bp.add_url_rule(
        rule='/',
        endpoint='index',
        view_func=route_handler('index', config),
        methods=['GET']
    )
    # Create (new)
    bp.add_url_rule(
        rule='/new',
        endpoint='create',
        view_func=route_handler('create', config),
        methods=['GET', 'POST']
    )
    # View
    bp.add_url_rule(
        rule='/<int:entity_id>',
        endpoint='view',
        view_func=route_handler('view', config),
        methods=['GET']
    )
    # Edit
    bp.add_url_rule(
        rule='/<int:entity_id>/edit',
        endpoint='edit',
        view_func=route_handler('edit', config),
        methods=['GET', 'POST']
    )
    # Delete
    bp.add_url_rule(
        rule='/<int:entity_id>/delete',
        endpoint='delete',
        view_func=route_handler('delete', config),
        methods=['POST']
    )


def register_auth_route(
    blueprint: Blueprint,
    url: str,
    handler: Callable,
    endpoint_name: str,
    methods: Optional[List[str]] = None
) -> None:
    """Register an authentication route on the given blueprint."""
    methods = methods or ['GET']
    blueprint.add_url_rule(
        rule=url,
        endpoint=endpoint_name,
        view_func=handler,
        methods=methods
    )
