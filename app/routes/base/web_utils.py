# app/routes/base/web_utils.py
import logging
from flask import Blueprint
from app.routes.base.components.template_renderer import render_safely, RenderSafelyConfig
from app.routes.base.components.context import SimpleContext, TableContext, EntityContext
from typing import Optional, List, Any, Callable, Dict, Tuple
from dataclasses import dataclass, field

from app.utils.table_helpers import get_plural_name

logger = logging.getLogger(__name__)


@dataclass
class CrudRouteConfig:
    blueprint: Any
    entity_name: str
    service: Optional[Any]
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
    title: str,
    url: str,
    template_path: str,
    context_provider: Callable,
    endpoint: str = None,
    methods: Optional[List[str]] = None,
    error_message: str = "Failed to load the page",
):
    """Register a route that renders a specific template with optional context."""
    # Prepare route configuration
    endpoint, methods = prepare_route_config(url, template_path, endpoint, methods)

    def route_handler(*args, **kwargs):
        """Handle requests to this route by rendering the template with context."""
        logger.info(f"Handling request for endpoint '{endpoint}' with args={args}, kwargs={kwargs}")

        try:
            # If a context provider was specified, call it to get template data
            if context_provider:
                logger.info(f"Calling context provider for endpoint '{endpoint}'")
                context = context_provider(*args, **kwargs)
                if not context:
                    logger.warning(f"Context provider returned None for endpoint '{endpoint}'")
                    context = SimpleContext(title=endpoint)
            else:
                logger.info(f"No context provider for endpoint '{endpoint}', using default SimpleContext")
                context = SimpleContext(title=endpoint)

            # Render the template safely, handling exceptions
            logger.info(f"Rendering with the following vars:")
            logger.info(f"template path: {template_path}")
            logger.info(f"context: {context}")

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
    """
    Registers standard CRUD routes for an entity on a Flask blueprint.

    This function creates and registers index, create, view, and edit routes for an entity.
    It handles template selection, context generation, and error message formation for each route.
    It also manages the pluralization of the entity name for display and URL construction.

    Args:
        crud_route_config (CrudRouteConfig): A configuration dataclass containing:
            - blueprint (flask.Blueprint): The Flask blueprint on which to register routes.
            - entity_name (str): The name of the entity for which routes are to be registered.
            - service (object, optional): An optional service with data access methods. If provided,
              it will be used to fetch entity data for view/edit routes. Defaults to None.
            - include_routes (List[str], optional): A list of route types to include.
              Defaults to ['index', 'create', 'view', 'edit'].
            - templates (Dict[str, str], optional): A dictionary of custom template paths keyed by
              route type. Defaults to {}.

    Returns:
        flask.Blueprint: The blueprint with the registered CRUD routes.
    """
    # Extract configuration parameters from the dataclass.
    logger.info("Starting registration of CRUD routes.")

    blueprint = crud_route_config.blueprint
    entity_name = crud_route_config.entity_name
    service = crud_route_config.service
    logger.info(f"Retrieved blueprint: {blueprint}")
    logger.info(f"Retrieved entity name: {entity_name}")
    logger.info(f"Retrieved service: {service}")

    if not isinstance(entity_name, str):
        logger.error("Invalid entity_name type; expected a string.")
        raise ValueError("The 'entity_name' must be a string.")

    # Ensure default routes and templates are applied if not provided.
    include_routes = crud_route_config.include_routes or ["index", "create", "view", "edit"]
    templates = crud_route_config.templates or {}
    logger.info(f"Using include_routes: {include_routes}")
    logger.info(f"Using templates: {templates}")

    logger.info(f"Registering CRUD routes for entity '{entity_name}' with routes {include_routes}")

    # Lowercase the entity name and determine its plural form for URLs and display.
    entity_name_lower = entity_name.lower()
    logger.info(f"Converted entity name to lowercase: {entity_name_lower}")

    # Direct context creation in dictionary
    context_providers = {
        "index": lambda: TableContext(
            table_name=entity_name,
            action="index"
        ),
        "create": lambda: EntityContext(
            action="create",
            table_name=entity_name
        ),
        "view": lambda entity_id: EntityContext(
            action="view",
            table_name=entity_name,
            entity_id=entity_id
        ),
        "edit": lambda entity_id: EntityContext(
            action="edit",
            table_name=entity_name,
            entity_id=entity_id,
            entity=service.get_by_id(entity_id) if service else None
        ),
    }
    logger.info("Context providers have been initialized.")

    # Define URL patterns for each route type.
    route_urls = {
        "index": "/",
        "create": "/create",
        "view": "/<int:entity_id>",
        "edit": "/<int:entity_id>/edit",
    }
    logger.info("URL patterns for routes have been defined.")

    # Iterate over the routes to be included and register each with the blueprint.
    for route_type in [r for r in include_routes if r in route_urls]:
        logger.info(f"Processing registration for route type: '{route_type}'")
        error_message = f"Failed to {route_type} {get_plural_name(entity_name) if route_type == 'index' else entity_name_lower}"
        logger.info(f"Error message set for route '{route_type}': {error_message}")

        # Use a custom template if provided; otherwise, determine the default template.
        template_path = templates.get(
            route_type, f"pages/tables/{get_plural_name(entity_name)}.html" if route_type == "index" else f"pages/crud/{route_type}.html"
        )
        logger.info(f"Using template '{template_path}' for route '{route_type}'")

        logger.info("Registering route with the following settings:")
        logger.info(f"  blueprint: {blueprint}")
        logger.info(f"  URL: {route_urls[route_type]}")
        logger.info(f"  endpoint: {route_type}")
        logger.info(f"  context_provider: {context_providers[route_type]}")

        register_route(
            blueprint=blueprint,
            url=route_urls[route_type],
            title="TBA",  # Title to be dynamically assigned later.
            template_path=template_path,
            endpoint=route_type,
            context_provider=context_providers[route_type],
            error_message=error_message,
        )
        logger.info(f"Successfully registered route '{route_type}'.")

    logger.info(f"Finished registering CRUD routes for entity '{entity_name}'.")
    return blueprint


def _create_default_context(entity_name, action, title):
    """Create a default context when no service is provided."""
    logger.info(f"No service provided for '{entity_name}'. Returning default TableContext.")
    return TableContext(action=action, table_name=entity_name, title=title)


def _handle_error(entity_name, entity_id, action, exception, title):
    """Handle exceptions during entity processing."""
    logger.error(f"Error getting context for {entity_name} ID={entity_id}: {exception}")
    # Return a minimal context that won't cause template errors
    return EntityContext(
        action=action,
        item={"id": entity_id, "error": f"Error loading {entity_name}: {str(exception)}"},
        error_message=f"Failed to load {entity_name}",
        title=title,
    )


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
