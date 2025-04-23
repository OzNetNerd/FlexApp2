import pkgutil
import importlib
from typing import Iterator, Any, Callable, Optional, Dict, List
from flask import Flask, Blueprint, request, redirect, url_for, abort
from dataclasses import dataclass
from enum import Enum

from app.utils.app_logging import get_logger
from app.utils.table_helpers import get_table_plural_name
from app.routes.web.components.template_renderer import render_safely, RenderSafelyConfig

logger = get_logger()

# -----------------------------------------------------------------
# Default template factory
# -----------------------------------------------------------------

def default_crud_templates(entity_table_name: str) -> 'CrudTemplates':
    """Generate default CRUD template paths for an entity."""
    plural = get_table_plural_name(entity_table_name)
    lower = entity_table_name.lower()
    return CrudTemplates(
        index=f"pages/tables/{plural}.html",
        create=f"pages/crud/create_{lower}.html",
        view=f"pages/crud/view_{lower}.html",
        edit=f"pages/crud/edit_{lower}.html",
    )

# -----------------------------------------------------------------
# CRUD route configuration classes
# -----------------------------------------------------------------

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

# -----------------------------------------------------------------
# Module discovery and registration
# -----------------------------------------------------------------

def discover_web_modules() -> Iterator[Any]:
    """Import and yield all modules in app.routes.web (excluding components)."""
    package = importlib.import_module('app.routes.web')
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        if module_name == 'components':
            continue
        yield importlib.import_module(f'{package.__name__}.{module_name}')


def register_web_blueprints(app: Flask) -> None:
    """Auto-wire CRUD routes and register web blueprints."""
    # Phase 1: wire CRUD routes
    for module in discover_web_modules():
        for attr in dir(module):
            if attr.endswith('_crud_config'):
                config = getattr(module, attr)
                if isinstance(config, CrudRouteConfig):
                    logger.debug(f"Wiring CRUD for {config.entity_table_name}")
                    register_crud_routes(config)

    # Phase 2: register blueprints
    for module in discover_web_modules():
        for attr in dir(module):
            if attr.endswith('_bp'):
                bp = getattr(module, attr)
                if isinstance(bp, Blueprint):
                    logger.debug(f"Registering blueprint: {bp.name} @ {bp.url_prefix}")
                    app.register_blueprint(bp)

# -----------------------------------------------------------------
# Core CRUD wiring and handler
# -----------------------------------------------------------------

def handle_crud_operation(
    endpoint: str,
    service: Any,
    blueprint_name: str,
    entity_id: Optional[int],
    form_data: Dict[str, Any]
) -> Any:
    """Perform create, edit, or delete operations and redirect appropriately."""
    if endpoint == 'create':
        entity = service.create(form_data)
        return redirect(url_for(f"{blueprint_name}.view", entity_id=entity.id))
    if endpoint == 'edit':
        entity = service.update(service.get_by_id(entity_id), form_data)
        return redirect(url_for(f"{blueprint_name}.view", entity_id=entity.id))
    if endpoint == 'delete':
        service.delete(entity_id)
        return redirect(url_for(f"{blueprint_name}.index"))
    return None


def route_handler(endpoint: str, config: CrudRouteConfig) -> Callable:
    """Return a Flask view function handling CRUD + safe rendering."""
    def handler(*args, **kwargs):
        logger.info(f"Handling {request.method} {endpoint} with args={args}, kwargs={kwargs}")

        # POST: CRUD operation
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

        # GET/others: render template safely
        template_path = config.templates.get(
            endpoint,
            f"pages/crud/{endpoint}_{config.entity_table_name.lower()}.html"
        )
        cfg = RenderSafelyConfig(
            template_path=template_path,
            context=config.__dict__,
            error_message=f"Error rendering {config.entity_table_name} {endpoint}",
            endpoint_name=endpoint
        )
        return render_safely(cfg)

    return handler


def register_crud_routes(config: CrudRouteConfig) -> None:
    """Attach CRUD routes (index/create/view/edit/delete) to blueprint."""
    bp = config.blueprint
    plural = get_table_plural_name(config.entity_table_name)
    base = f"/{plural}"

    bp.route(base, methods=['GET'])(route_handler('index', config))
    bp.route(f"{base}/new", methods=['GET', 'POST'])(route_handler('create', config))
    bp.route(f"{base}/<int:entity_id>", methods=['GET'])(route_handler('view', config))
    bp.route(f"{base}/<int:entity_id>/edit", methods=['GET', 'POST'])(route_handler('edit', config))
    bp.route(f"{base}/<int:entity_id>/delete", methods=['POST'])(route_handler('delete', config))

# -----------------------------------------------------------------
# Auth route registration
# -----------------------------------------------------------------

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
