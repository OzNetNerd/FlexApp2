# web/route_registration.py

import jinja2.exceptions
import logging
from typing import Callable, List, Optional, Any, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
from flask import Blueprint, request, flash, redirect, url_for, render_template

from app.utils.table_helpers import get_table_plural_name
from app.routes.web.context import SimpleContext, EntityContext, TableContext

logger = logging.getLogger(__name__)


class CRUDEndpoint(Enum):
    EDIT = "edit"
    CREATE = "create"
    DELETE = "delete"

    @classmethod
    def is_valid(cls, endpoint: str) -> bool:
        return any(endpoint == item.value for item in cls)


@dataclass
class RenderSafelyConfig:
    template_path: str
    context: Any
    error_message: str
    endpoint: str


@dataclass
class CrudTemplates:
    index: Optional[str] = None
    create: Optional[str] = None
    view: Optional[str] = None
    edit: Optional[str] = None
    delete: Optional[str] = None

    def get(self, route_type: str, default: str) -> str:
        """Get the template path for the given route type or return the default."""
        template = getattr(self, route_type, None)
        return template if template is not None else default

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert the dataclass to a dictionary."""
        return {"index": self.index, "create": self.create, "view": self.view, "edit": self.edit, "delete": self.delete}


@dataclass
class CrudRouteConfig:
    blueprint: Blueprint
    entity_table_name: str
    service: Any
    templates: Optional[CrudTemplates] = None
    include_routes: Optional[List[str]] = None


def render_safely(config: RenderSafelyConfig):
    """Safely render a template with error handling."""
    try:
        logger.info(f"Attempting to render template: {config.template_path}")
        return render_template(config.template_path, **config.context.to_dict())
    except jinja2.exceptions.TemplateNotFound as e:
        # Re-raise template not found errors
        logger.error(f"Template not found: '{config.template_path}'")
        raise  # Re-raise the exception
    except Exception as e:
        logger.error(f"Error rendering template '{config.template_path}': {e}", exc_info=True)
        return f"<h1>{config.error_message}</h1><p>Error: {str(e)}</p>", 500


def prepare_route_config(
    url: str, template_path: str, endpoint: Optional[str] = None, methods: Optional[List[str]] = None
) -> Tuple[str, List[str]]:
    """Prepare route configuration with defaults."""
    endpoint = endpoint or url.lstrip("/").replace("/", "_")
    methods = methods or ["GET", "POST"]
    return endpoint, methods


def find_service(context_provider: Callable) -> Optional[Any]:
    """Find a service object in a callable's closure or defaults."""
    if not context_provider:
        return None

    def is_service(obj: Any) -> bool:
        return hasattr(obj, "get_by_id") and hasattr(obj, "update") and hasattr(obj, "create") and hasattr(obj, "delete")

    # Check closure
    if hasattr(context_provider, "__closure__") and context_provider.__closure__:
        for closure in context_provider.__closure__:
            obj = closure.cell_contents
            if is_service(obj):
                logger.info("Found service in context_provider's closure")
                return obj

    # Check defaults
    if hasattr(context_provider, "__defaults__") and context_provider.__defaults__:
        for obj in context_provider.__defaults__:
            if is_service(obj):
                logger.info("Found service in context_provider's defaults")
                return obj

    return None


def handle_crud_operation(
    endpoint: str, service: Any, blueprint_name: str, entity_id: Optional[str], form_data: Dict[str, Any]
) -> Optional[Any]:
    """Handle CRUD operations based on endpoint type."""
    if not service:
        logger.error(f"No service available for {endpoint}")
        flash("Error: Service not available for this operation", "error")
        return redirect(url_for(f"{blueprint_name}.index"))

    if endpoint == CRUDEndpoint.EDIT.value and entity_id:
        entity = service.get_by_id(entity_id)
        service.update(entity, form_data)
        flash("Successfully updated record", "success")
        return redirect(url_for(f"{blueprint_name}.view", entity_id=entity_id))

    elif endpoint == CRUDEndpoint.CREATE.value:
        new_entity = service.create(form_data)
        flash("Successfully created record", "success")
        entity_id = getattr(new_entity, "entity_id", None)

        if entity_id:
            return redirect(url_for(f"{blueprint_name}.view", entity_id=entity_id))
        return redirect(url_for(f"{blueprint_name}.index"))

    elif endpoint == CRUDEndpoint.DELETE.value and entity_id:
        service.delete(entity_id)
        flash("Successfully deleted record", "success")
        return redirect(url_for(f"{blueprint_name}.index"))

    return None


def get_context(context_provider: Optional[Callable], title: str, args: tuple, kwargs: dict) -> Any:
    """Get context from provider or return a simple context."""
    if not context_provider:
        logger.info("No context provider, using default SimpleContext")
        return SimpleContext(title=title)

    try:
        if isinstance(context_provider, type):
            logger.info(f"Context provider is a class, instantiating with title: {title}")
            context = context_provider(title=title)
        else:
            context = context_provider(*args, **kwargs)

        if not context:
            logger.warning("Context provider returned None")
            return SimpleContext(title=title)

        return context
    except Exception as e:
        logger.error(f"Error getting context: {e}", exc_info=True)
        return SimpleContext(title=title)


def register_route(
    blueprint: Blueprint,
    url: str,
    template_path: str,
    context_provider: Callable,
    title: Optional[str] = None,
    endpoint: Optional[str] = None,
    methods: Optional[List[str]] = None,
    error_message: str = "Failed to load the page",
):
    """Register a route with the given blueprint."""
    logger.info(f"Starting route registration - URL: {url}, Template: {template_path}")

    # Prepare route configuration
    endpoint, methods = prepare_route_config(url, template_path, endpoint, methods)
    logger.info(f"Prepared route configuration - Endpoint: {endpoint}, Methods: {methods}")

    # Set title
    title = title or endpoint
    logger.info(f"Using title '{title}' for the route")

    logger.info(f"Registering route - title: {title} - endpoint: {endpoint}")

    def route_handler(*args, **kwargs):
        """Handle HTTP requests for this route."""
        logger.info(f"Handling request for endpoint '{endpoint}' with args: {args}, kwargs: {kwargs}")

        try:
            # Handle CRUD operations
            if request.method == "POST" and CRUDEndpoint.is_valid(endpoint):
                logger.info(f"Handling POST request for endpoint '{endpoint}'")
                entity_id = kwargs.get("entity_id")
                form_data = request.form.to_dict()
                service = find_service(context_provider)

                logger.info(f"Found service '{service}' for the operation")
                result = handle_crud_operation(endpoint, service, blueprint.name, entity_id, form_data)

                if result:
                    logger.info(f"CRUD operation successful, returning result")
                    return result

            # Get context and render template
            context = get_context(context_provider, title, args, kwargs)
            logger.info(f"Context prepared for template rendering - Context: {context}")

            logger.info(f"CRITICAL: About to render '{template_path}' for endpoint '{endpoint}'")
            logger.info(f"Blueprint name: {blueprint.name}, URL values: {kwargs}")

            result = render_safely(
                RenderSafelyConfig(
                    template_path,
                    context,
                    error_message,
                    endpoint,
                )
            )

            if result is None:
                logger.error("Template renderer returned None")
                return f"<h1>Error rendering template</h1>", 500

            logger.info(f"Template rendered successfully for endpoint '{endpoint}'")
            return result

        except ValueError as ve:
            logger.error(f"ValueError: {ve}")
            return f"<h1>Error in route handler</h1><p>{str(ve)}</p>", 500
        except Exception as e:
            logger.error(f"Exception: {e}", exc_info=True)
            return f"<h1>Unexpected error</h1><p>{str(e)}</p>", 500

    # Register route with blueprint
    route_handler.__name__ = endpoint
    blueprint.add_url_rule(url, endpoint=endpoint, view_func=route_handler, methods=methods)
    logger.info(f"Registered route '{endpoint}' at '{url}' with methods {methods}")

    return route_handler


def register_crud_routes(crud_route_config: CrudRouteConfig) -> Any:
    """Register CRUD routes based on configuration."""
    logger.info("Starting registration of CRUD routes.")

    blueprint = crud_route_config.blueprint
    entity_table_name = crud_route_config.entity_table_name
    service = crud_route_config.service

    if not isinstance(entity_table_name, str):
        logger.error("Invalid entity_table_name type; expected a string.")
        raise ValueError("The 'entity_table_name' must be a string.")

    logger.info(f"Entity table name is valid: {entity_table_name}")

    include_routes = crud_route_config.include_routes or ["index", "create", "view", "edit", "update", "delete"]
    templates = crud_route_config.templates or CrudTemplates()

    logger.info(f"Routes to include: {include_routes}")
    logger.info(f"Templates configuration: {templates}")

    entity_table_plural_name = get_table_plural_name(entity_table_name)

    logger.info(f"Plural name for the entity table '{entity_table_name}': {entity_table_plural_name}")

    # Consolidate all route configuration in one place
    route_configs = {
        "index": {
            "url": "/",
            "template_default": f"pages/tables/{entity_table_plural_name}.html",
            "error_message": f"Failed to index {entity_table_plural_name}",
            "context_provider": lambda: TableContext(
                entity_table_name=entity_table_name,
                action="index",
                title=entity_table_plural_name.capitalize(),
            ),
            "methods": ["GET"],
        },
        "create": {
            "url": "/create",
            "template_default": f"pages/crud/create.html",
            "error_message": f"Failed to create {entity_table_name}",
            "context_provider": lambda service=service: EntityContext(
                action="create", entity_table_name=entity_table_name, title=f"Create {entity_table_name}", read_only=False
            ),
            "methods": ["GET", "POST"],
        },
        "view": {
            "url": "/<int:entity_id>",
            "template_default": f"pages/crud/view.html",
            "error_message": f"Failed to view {entity_table_name}",
            "context_provider": lambda entity_id: EntityContext(
                action="view",
                entity_table_name=entity_table_name,
                entity=service.get_by_id(entity_id),
                title=f"View {entity_table_name}",
            ),
            "methods": ["GET"],
        },
        "edit": {
            "url": "/<int:entity_id>/edit",
            "template_default": f"pages/crud/edit.html",
            "error_message": f"Failed to edit {entity_table_name}",
            "context_provider": lambda entity_id: EntityContext(
                action="edit",
                entity_table_name=entity_table_name,
                entity_id=entity_id,
                entity=service.get_by_id(entity_id),  # Make sure entity is fetched correctly
                title=f"Edit {entity_table_name}",
                read_only=False,
                blueprint_name=blueprint.name,
                # This will be fixed by our update to _initialize_derived_fields
                submit_url=url_for(f"{blueprint.name}.update", entity_id=entity_id),
            ),
            "methods": ["GET", "POST"],
        },
        "update": {
            "url": "/<int:entity_id>/update",
            "template_default": f"pages/crud/edit.html",
            "error_message": f"Failed to update {entity_table_name}",
            "context_provider": lambda entity_id, service=service: EntityContext(
                action="update",
                entity_table_name=entity_table_name,
                entity_id=entity_id,
                entity=service.get_by_id(entity_id),
                title=f"Update {entity_table_name}",
                read_only=False,
            ),
            "methods": ["POST"],
        },
        "delete": {
            "url": "/<int:entity_id>/delete",
            "template_default": f"pages/crud/delete.html",
            "error_message": f"Failed to delete {entity_table_name}",
            "context_provider": lambda entity_id: EntityContext(
                action="delete",
                entity_table_name=entity_table_name,
                entity_id=entity_id,
                entity=service.get_by_id(entity_id),
                title=f"Delete {entity_table_name}",
                read_only=True,
                blueprint_name=blueprint.name,
            ),
            "methods": ["GET", "POST"],
        },
    }

    # Register routes based on configuration
    for route_type in [r for r in include_routes if r in route_configs]:
        config = route_configs[route_type]
        logger.info(f"Processing registration for route type: '{route_type}'")

        template_path = templates.get(route_type, config["template_default"])

        logger.info(f"For route '{route_type}', using template: {template_path}")
        logger.info(f"Custom template was: {templates.get(route_type, 'Not found')}")

        logger.info(f"Registering route '{route_type}' with URL: {config['url']}")

        register_route(
            blueprint=blueprint,
            url=config["url"],
            template_path=template_path,
            endpoint=route_type,
            context_provider=config["context_provider"],
            error_message=config["error_message"],
            methods=config.get("methods", ["GET"]),
        )

        logger.info(f"Successfully registered route '{route_type}'.")

    logger.info("CRUD route registration completed successfully.")
    return blueprint


def register_auth_route(blueprint: Blueprint, url: str, handler: Callable, endpoint: str, methods: Optional[List[str]] = None):
    """Register an authentication route with a custom handler."""
    if methods is None:
        methods = ["GET"]
        logger.info(f"No methods provided for auth route '{endpoint}', defaulting to ['GET']")

    logger.info(f"Registering auth route '{endpoint}' at '{url}' with methods {methods}")
    blueprint.add_url_rule(url, endpoint=endpoint, view_func=handler, methods=methods)
    logger.info(f"Registered auth route '{endpoint}' at '{url}'")

    return blueprint
