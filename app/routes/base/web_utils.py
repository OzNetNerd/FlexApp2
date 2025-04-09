# app/routes/base/web_utils.py
import logging
from flask import url_for, redirect, flash, Blueprint, request
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import SimpleContext, TableContext, EntityContext
from typing import Optional, List, Any, Callable, Dict, Union, Tuple

logger = logging.getLogger(__name__)


def prepare_route_config(
        url: str,
        template_path: str,
        endpoint: str = None,
        methods: Optional[List[str]] = None
) -> Tuple[str, List[str]]:
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

    Examples:
        >>> prepare_route_config('/users', 'users/index.html')
        ('users_index', ['GET'])

        >>> prepare_route_config('/login', 'auth/login.html', methods=['GET', 'POST'])
        ('auth_login', ['GET', 'POST'])

        >>> prepare_route_config('/profile', 'profile.html', endpoint='user_profile')
        ('user_profile', ['GET'])
    """
    logger.info(f"Preparing route configuration for URL '{url}' with template '{template_path}'")

    # Set default methods if not provided
    if not methods:
        methods = ["GET"]
        logger.info(f"No 'methods' param provided for '{url}'. Defaulting to: {methods}")
    else:
        logger.info(f"Route '{url}' configured with methods: {methods}")

    # Auto-generate endpoint name if none provided
    if not endpoint:
        # Split template path to get component parts
        parts = template_path.split('/')

        if len(parts) > 1:
            # For nested templates (e.g., "users/profile.html"),
            # combine the directory and filename without extension
            endpoint = f"{parts[-2]}_{parts[-1].split('.')[0]}"
            logger.info(f"Derived endpoint from nested template: '{parts[-2]}_{parts[-1].split('.')[0]}'")
        else:
            # For top-level templates (e.g., "home.html"),
            # just use the filename without extension
            endpoint = template_path.split('.')[0]
            logger.info(f"Derived endpoint from root template: '{template_path.split('.')[0]}'")

        logger.info(f"No endpoint provided. Using derived endpoint: '{endpoint}'")
    else:
        logger.info(f"Using provided endpoint: '{endpoint}'")

    logger.info(f"Route configuration prepared: URL='{url}', endpoint='{endpoint}', methods={methods}")
    return endpoint, methods


def register_page_route(
        blueprint: Blueprint,
        title: str,
        url: str,
        template_path: str,
        endpoint: str = None,
        methods: Optional[List[str]] = None,
        context_provider: Optional[Callable] = None,
        error_message: str = "Failed to load the page",
):
    """Register a route that renders a specific template with optional context."""
    # Prepare route configuration
    endpoint, methods = prepare_route_config(url, template_path, endpoint, methods)

    def route_handler(*args, **kwargs):
        """Handle requests to this route by rendering the template with context."""
        logger.info(f"Handling request for endpoint '{endpoint}' with args={args}, kwargs={kwargs}")

        # If a context provider was specified, call it to get template data
        if context_provider:
            logger.info(f"Calling context provider for endpoint '{endpoint}'")
            context = context_provider(title=title, *args, **kwargs)
            if not context:
                logger.warning(f"Context provider returned None for endpoint '{endpoint}'")
                context = SimpleContext(title=endpoint)
        else:
            logger.info(f"No context provider for endpoint '{endpoint}', using default SimpleContext")
            context = SimpleContext(title=endpoint)

        # Render the template safely, handling exceptions
        return render_safely(
            template_path,
            context,
            error_message,
            endpoint_name=endpoint
        )

    # Set the function name for Flask (needed for proper endpoint registration)
    route_handler.__name__ = endpoint

    # Register the route with Flask
    blueprint.add_url_rule(
        url,
        endpoint=endpoint,
        view_func=route_handler,
        methods=methods
    )

    logger.info(f"Registered route '{endpoint}' at '{url}' for template '{template_path}' with methods {methods}")

    return route_handler


def register_crud_routes(
        blueprint: Blueprint,
        entity_name: str,
        service=None,
        templates: Optional[Dict[str, str]] = None,
        include_routes: Optional[List[str]] = None
):
    """Register standard CRUD routes for an entity.

    Args:
        blueprint (Blueprint): The Flask blueprint
        entity_name (str): Name of the entity (e.g., 'user', 'product')
        service (object, optional): Service object with standard methods
        templates (dict, optional): Dict of {route_type: template_path}
        include_routes (list, optional): List of route types to include
                                         Defaults to ['index', 'create', 'view', 'edit']

    Returns:
        Blueprint: The blueprint with routes registered
    """
    if include_routes is None:
        include_routes = ['index', 'create', 'view', 'edit']
        logger.info(f"No include_routes provided. Defaulting to {include_routes} for '{entity_name}'")

    if templates is None:
        templates = {}
        logger.info(f"No templates provided. Using default templates for '{entity_name}'")

    logger.info(f"Registering CRUD routes for entity '{entity_name}'")

    plural_mapping = {
        "company": "companies",
        "opportunity": "opportunities",
        "category": "categories",
        "capability": "capabilities",
        "home": "home",
    }

    entity_name_lower = entity_name.lower()
    plural_form = plural_mapping.get(entity_name_lower, f"{entity_name_lower}s")
    logger.info(f"Plural form for '{entity_name}': '{plural_form}'")

    default_templates = {
        'index': f"pages/tables/{plural_form}.html",  # Updated to use the mapped plural form.
        'create': "pages/crud/create.html",
        'view': "pages/crud/view.html",
        'edit': "pages/crud/edit.html"
    }

    url_patterns = {
        'index': '/',
        'create': '/create',
        'view': '/<int:entity_id>',
        'edit': '/<int:entity_id>/edit'
    }

    context_providers = {
        'index': lambda title=None, **kwargs: TableContext(
            title=f"{entity_name.title()}s",
            table_name=entity_name
        ),
        'create': lambda title=None, **kwargs: TableContext(
            action="Create",
            table_name=entity_name
        ),
        'view': lambda entity_id, title=None, **kwargs: _get_entity_context(
            service, entity_name, entity_id, "View"
        ) if service else TableContext(
            action="View",
            table_name=entity_name
        ),
        'edit': lambda entity_id, title=None, **kwargs: _get_entity_context(
            service, entity_name, entity_id, "Edit"
        ) if service else TableContext(
            action="Edit",
            table_name=entity_name
        )
    }

    error_messages = {
        'index': f"Failed to load {plural_form}.",
        'create': f"Failed to load create {entity_name_lower} form.",
        'view': f"Failed to load {entity_name_lower} details.",
        'edit': f"Failed to load edit {entity_name_lower} form."
    }

    for route_type in include_routes:
        if route_type in ['index', 'create', 'view', 'edit']:
            template = templates.get(route_type, default_templates.get(route_type))
            logger.info(f"Registering '{route_type}' route for '{entity_name}' using template '{template}'")

            register_page_route(
                blueprint=blueprint,
                url=url_patterns[route_type],
                title="TBA",
                template_path=template,
                endpoint=route_type,
                context_provider=context_providers[route_type],
                error_message=error_messages[route_type]
            )

    logger.info(f"Finished registering CRUD routes for '{entity_name}'")
    return blueprint




def _get_entity_context(service, entity_name, entity_id, action, title=""):
    """Helper to get context for item detail routes.

    Args:
        service: Service with get_by_id method
        entity_name (str): Name of the entity
        entity_id: ID of the item to retrieve
        action (str): Action being performed ('View', 'Edit', etc.)
        title (str): Optional title for the page

    Returns:
        TableContext or redirect
    """
    logger.info(f"Getting context for entity '{entity_name}', ID={entity_id}, action='{action}'")

    if not service:
        logger.info(f"No service provided for '{entity_name}'. Returning default TableContext.")
        return TableContext(action=action, table_name=entity_name, title=title)

    try:
        item = service.get_by_id(entity_id)
        logger.info(f"Service call to get '{entity_name}' by ID={entity_id} returned: {'found' if item else 'not found'}")

        if not item:
            flash(f"{entity_name.title()} not found.", "danger")
            redirect_target = url_for(f"{entity_name.lower()}s.index")
            logger.info(f"Redirecting to '{redirect_target}' due to missing item")
            return redirect(redirect_target)

        # Safe conversion of item to dictionary
        try:
            if hasattr(item, 'to_dict'):
                item_data = item.to_dict()
            elif hasattr(item, '__table__'):
                # SQLAlchemy model - get column values
                item_data = {}
                for column in item.__table__.columns:
                    item_data[column.name] = getattr(item, column.name)
            else:
                # Last resort - try to convert object vars to dict
                item_data = vars(item)
        except Exception as e:
            logger.error(f"Error converting {entity_name} to dictionary: {e}")
            # Fallback with minimal data
            item_data = {'id': getattr(item, 'id', entity_id), 'error': 'Unable to convert item to dictionary'}

        logger.info(f"Context prepared for '{entity_name}' ID={entity_id} with action '{action}'")

        return EntityContext(
            action=action,
            # table_name=entity_name,
            item=item_data,
            title=title
        )
    except Exception as e:
        logger.error(f"Error getting context for {entity_name} ID={entity_id}: {e}")
        # Return a minimal context that won't cause template errors
        return EntityContext(
            action=action,
            # table_name=entity_name,
            item={'id': entity_id, 'error': f"Error loading {entity_name}: {str(e)}"},
            error_message=f"Failed to load {entity_name}",
            title=title
        )

def register_auth_route(
        blueprint: Blueprint,
        url: str,
        handler: Callable,
        endpoint: str,
        methods: Optional[List[str]] = None
):
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

    blueprint.add_url_rule(
        url,
        endpoint=endpoint,
        view_func=handler,
        methods=methods
    )

    logger.info(f"Registered auth route '{endpoint}' at '{url}'")

    return blueprint