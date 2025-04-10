# app/routes/base/web_utils.py
import logging
from flask import Blueprint
from mypy.dmypy.client import action

from app.routes.base.components.template_renderer import render_safely, RenderSafelyConfig
from app.routes.base.components.context import SimpleContext, TableContext, EntityContext
from typing import Optional, List, Any, Callable, Dict, Tuple
from dataclasses import dataclass, field

from app.utils.table_helpers import get_table_plural_name
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)


@dataclass
class CrudRouteConfig:
    blueprint: Blueprint
    entity_table_name: str
    service: CRUDService
    include_routes: List[str] = field(default_factory=lambda: ["index", "create", "view", "edit"])
    templates: Dict[str, str] = field(default_factory=dict)


def prepare_route_config(url: str, template_path: str, endpoint: str = None, methods: Optional[List[str]] = None) -> Tuple[str, List[str]]:
    """Prepares Flask route configuration by setting defaults and deriving endpoint names.

    This utility function handles common route configuration tasks, providing
    sensible defaults and deriving endpoint names from template paths when not
    explicitly provided. It ensures consistent route configuration across the
    application and centralizes the endpoint name generation logic.

    Args:
        url: URL pattern for the route (e.g., '/', '/users/<int:user_id>')
        template_path: Path to the template file to render (e.g., 'home.html',
            'users/profile.html')
        endpoint: Optional custom endpoint name. If not provided, one will be
            derived from template_path following naming conventions
        methods: Optional list of HTTP methods the route responds to. Defaults
            to ["GET"] if not specified

    Returns:
        tuple: A tuple containing (endpoint_name, methods_list) where:
            - endpoint_name (str): The final endpoint name (either provided or derived)
            - methods_list (List[str]): The final list of HTTP methods

    """
    logger.info(f"Preparing route configuration for URL '{url}' with template '{template_path}'")

    # Set default methods if not provided
    if not methods:
        methods = ["GET"]
        logger.warning(f"No 'methods' param provided for '{url}'. Defaulting to: {methods}")
    else:
        logger.info(f"Route '{url}' configured with methods: {methods}")

    # Auto-generate endpoint name if none provided
    if not endpoint:
        # Split template path to get component parts
        parts = template_path.split("/")

        if len(parts) > 1:
            # For nested templates (e.g., "users/profile.html"),
            # combine the directory and filename without extension
            endpoint = f"{parts[-2]}_{parts[-1].split('.')[0]}"
            logger.info(f"Derived endpoint from nested template: '{parts[-2]}_{parts[-1].split('.')[0]}'")
        else:
            # For top-level templates (e.g., "home.html"),
            # just use the filename without extension
            endpoint = template_path.split(".")[0]
            logger.info(f"Derived endpoint from root template: '{template_path.split('.')[0]}'")

        logger.info(f"No endpoint provided. Using derived endpoint: '{endpoint}'")
    else:
        logger.info(f"Using provided endpoint: '{endpoint}'")

    logger.info(f"Route configuration prepared: URL='{url}', endpoint='{endpoint}', methods={methods}")
    return endpoint, methods


def register_route(
        blueprint: Blueprint,
        url: str,
        template_path: str,
        context_provider: Callable,
        title: str = None,
        endpoint: str = None,
        methods: Optional[List[str]] = None,
        error_message: str = "Failed to load the page",
):
    """Register a route that renders a specific template with optional context."""
    # Prepare route configuration
    endpoint, methods = prepare_route_config(url, template_path, endpoint, methods)
    logger.info(f'debugger - title: {title} - endpoint: {endpoint}')
    title = title or endpoint

    def route_handler(*args, **kwargs):
        """Handle requests to this route by rendering the template with context."""
        logger.info(f"Handling request for endpoint '{endpoint}' with args={args}, kwargs={kwargs}")

        try:
            # If a context provider was specified, call it to get template data
            if context_provider:
                logger.info(f"Calling context provider ({context_provider}) for endpoint '{endpoint}'")

                # Check if context_provider is a class (like SimpleContext)
                if isinstance(context_provider, type):
                    # It's a class, instantiate it with title
                    logger.info(f"Context provider is a class, instantiating with title: {title}")
                    context = context_provider(title=title)
                else:
                    # It's a function (lambda or regular), call it normally
                    context = context_provider(*args, **kwargs)

                if not context:
                    logger.warning(f"Context provider returned None for endpoint '{endpoint}'")
                    context = SimpleContext(title=title)
            else:
                logger.info(f"No context provider for endpoint '{endpoint}', using default SimpleContext")
                context = SimpleContext(title=title)

            # Render the template safely, handling exceptions
            logger.info(f"Rendering with the following vars:")
            logger.info(f"template path: {template_path}")
            logger.info(f"Context: {context}")

            return render_safely(RenderSafelyConfig(
                template_path,
                context,
                error_message,
                endpoint,
            ))
        except ValueError as ve:
            # Properly handle ValueError by returning an error page
            logger.error(f"ValueError in route handler for endpoint '{endpoint}': {ve}")
            return f"<h1>Error in route handler</h1><p>{str(ve)}</p>", 500

    # Set the function name for Flask (needed for proper endpoint registration)
    route_handler.__name__ = endpoint

    # Register the route with Flask
    blueprint.add_url_rule(url, endpoint=endpoint, view_func=route_handler, methods=methods)

    logger.info(f"Registered route '{endpoint}' at '{url}' for template '{template_path}' with methods {methods}")

    return route_handler


def register_crud_routes(crud_route_config: CrudRouteConfig) -> Any:
    # Extract configuration parameters
    logger.info("Starting registration of CRUD routes.")
    blueprint = crud_route_config.blueprint
    entity_table_name = crud_route_config.entity_table_name
    service = crud_route_config.service

    if not isinstance(entity_table_name, str):
        logger.error("Invalid entity_table_name type; expected a string.")
        raise ValueError("The 'entity_table_name' must be a string.")

    include_routes = crud_route_config.include_routes or ["index", "create", "view", "edit"]
    templates = crud_route_config.templates or {}

    entity_table_plural_name = get_table_plural_name(entity_table_name)

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
        },
        "create": {
            "url": "/create",
            "template_default": f"pages/crud/create.html",
            "error_message": f"Failed to create {entity_table_name}",
            "context_provider": lambda: EntityContext(
                action="create",
                entity_table_name=entity_table_name,
                title=f"Create {entity_table_name}",
            ),
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
        },
        "edit": {
            "url": "/<int:entity_id>/edit",
            "template_default": f"pages/crud/edit.html",
            "error_message": f"Failed to edit {entity_table_name}",
            "context_provider": lambda entity_id: EntityContext(
                action="edit",
                entity_table_name=entity_table_name,
                entity_id=entity_id,
                entity=service.get_by_id(entity_id),
                title=f"Edit {entity_table_name}",
            ),
        },
    }

    # Register routes based on configuration
    for route_type in [r for r in include_routes if r in route_configs]:
        config = route_configs[route_type]
        logger.info(f"Processing registration for route type: '{route_type}'")

        template_path = templates.get(route_type, config["template_default"])

        register_route(
            blueprint=blueprint,
            url=config["url"],
            template_path=template_path,
            endpoint=route_type,
            context_provider=config["context_provider"],
            error_message=config["error_message"],
        )
        logger.info(f"Successfully registered route '{route_type}'.")

    return blueprint

def register_auth_route(blueprint: Blueprint, url: str, handler: Callable, endpoint: str, methods: Optional[List[str]] = None):
    """Register an authentication route with a custom handler.

    Args:
        blueprint (Blueprint): The Flask blueprint
        url (str): URL pattern for the route
        handler (Callable): Function that handles the route
        endpoint (str): Endpoint name
        methods (list, optional): HTTP methods
    """
    if methods is None:
        methods = ["GET"]
        logger.info(f"No methods provided for auth route '{endpoint}', defaulting to ['GET']")

    logger.info(f"Registering auth route '{endpoint}' at '{url}' with methods {methods}")

    blueprint.add_url_rule(url, endpoint=endpoint, view_func=handler, methods=methods)

    logger.info(f"Registered auth route '{endpoint}' at '{url}'")

    return blueprint
