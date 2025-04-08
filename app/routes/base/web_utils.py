# app/routes/base/web_utils.py
import logging
from flask import url_for, redirect, flash, Blueprint, request
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import SimpleContext
from typing import Optional, List, Any, Callable, Dict, Union

logger = logging.getLogger(__name__)


def register_page_route(
        blueprint: Blueprint,
        url: str,
        template_path: str,
        endpoint: Optional[str] = None,
        methods: Optional[List[str]] = None,
        context_provider: Optional[Callable] = None,
        error_message: str = "Failed to load the page"
):
    """Register a route that renders a specific template with optional context.

    Args:
        blueprint (Blueprint): The Flask blueprint
        url (str): URL pattern for the route (e.g., '/', '/<int:item_id>')
        template_path (str): Path to the template to render
        endpoint (str, optional): Endpoint name (defaults to derived from URL)
        methods (list, optional): HTTP methods (defaults to ["GET"])
        context_provider (Callable, optional): Function that returns context data
        error_message (str): Error message if rendering fails

    Returns:
        function: The registered route handler
    """
    if methods is None:
        methods = ["GET"]

    # Create endpoint name if not provided
    if not endpoint:
        # Try to derive from template path
        parts = template_path.split('/')
        if len(parts) > 1:
            endpoint = f"{parts[-2]}_{parts[-1].split('.')[0]}"
        else:
            endpoint = template_path.split('.')[0]

    def route_handler(*args, **kwargs):
        # Get context from provider or use empty SimpleContext
        context = SimpleContext()
        if context_provider:
            # Pass all route args/kwargs to the context provider
            provided_context = context_provider(*args, **kwargs)
            if provided_context is not None:
                context = provided_context

        return render_safely(
            template_path,
            context,
            error_message,
            endpoint_name=endpoint
        )

    # Set function name for better debugging
    route_handler.__name__ = endpoint

    # Register the route
    blueprint.add_url_rule(
        url,
        endpoint=endpoint,
        view_func=route_handler,
        methods=methods
    )

    logger.info(f"Registered route '{endpoint}' at '{url}' for template '{template_path}'")

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

    if templates is None:
        templates = {}

    # Default templates
    default_templates = {
        'index': f"pages/tables/{entity_name}s.html",
        'create': f"pages/crud/create.html",
        'view': f"pages/crud/view.html",
        'edit': f"pages/crud/edit.html"
    }

    # Mapping for irregular plurals
    plural_mapping = {
        "company": "companies",
        "opportunity": "opportunities",
        "category": "categories",
        "capability": "capabilities",
        "home": "home",
    }

    # URL patterns
    url_patterns = {
        'index': '/',
        'create': '/create',
        'view': '/<int:item_id>',
        'edit': '/<int:item_id>/edit'
    }

    # Plural form for display
    entity_name_lower = entity_name.lower()
    plural_form = plural_mapping.get(entity_name_lower, f"{entity_name_lower}s")

    # Configure context providers for each route type
    context_providers = {
        'index': lambda: SimpleContext(
            title=f"{entity_name.title()}s",
            table_name=entity_name
        ),
        'create': lambda: SimpleContext(
            action="Create",
            table_name=entity_name
        ),
        'view': lambda item_id: _get_item_context(
            service, entity_name, item_id, "View"
        ) if service else SimpleContext(
            action="View",
            table_name=entity_name
        ),
        'edit': lambda item_id: _get_item_context(
            service, entity_name, item_id, "Edit"
        ) if service else SimpleContext(
            action="Edit",
            table_name=entity_name
        )
    }

    # Error messages
    error_messages = {
        'index': f"Failed to load {plural_form}.",
        'create': f"Failed to load create {entity_name_lower} form.",
        'view': f"Failed to load {entity_name_lower} details.",
        'edit': f"Failed to load edit {entity_name_lower} form."
    }

    # Register each route
    for route_type in include_routes:
        if route_type in ['index', 'create', 'view', 'edit']:
            template = templates.get(route_type, default_templates.get(route_type))

            register_page_route(
                blueprint=blueprint,
                url=url_patterns[route_type],
                template_path=template,
                endpoint=route_type,
                context_provider=context_providers[route_type],
                error_message=error_messages[route_type]
            )

    return blueprint


def _get_item_context(service, entity_name, item_id, action):
    """Helper to get context for item detail routes.

    Args:
        service: Service with get_by_id method
        entity_name (str): Name of the entity
        item_id: ID of the item to retrieve
        action (str): Action being performed ('View', 'Edit', etc.)

    Returns:
        SimpleContext or redirect
    """
    if not service:
        return SimpleContext(action=action, table_name=entity_name)

    item = service.get_by_id(item_id)

    if not item:
        flash(f"{entity_name.title()} not found.", "danger")
        return redirect(url_for(f"{entity_name.lower()}s.index"))

    # Convert entity object to dictionary if it has to_dict method
    item_data = item.to_dict() if hasattr(item, 'to_dict') else item

    return SimpleContext(
        action=action,
        table_name=entity_name,
        item=item_data
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

    blueprint.add_url_rule(
        url,
        endpoint=endpoint,
        view_func=handler,
        methods=methods
    )

    logger.info(f"Registered auth route '{endpoint}' at '{url}'")

    return blueprint


def register_auth_conditional_route(
        blueprint: Blueprint,
        url: str,
        authenticated_template: str,
        unauthenticated_template: str,
        endpoint: str,
        methods: Optional[List[str]] = None
):
    """Register a route that renders different templates based on auth status.

    Args:
        blueprint (Blueprint): The Flask blueprint
        url (str): URL pattern for the route
        authenticated_template (str): Template path for authenticated users
        unauthenticated_template (str): Template path for unauthenticated users
        endpoint (str): Endpoint name
        methods (list, optional): HTTP methods
    """
    from flask_login import current_user

    if methods is None:
        methods = ["GET"]

    def route_handler(*args, **kwargs):
        template = authenticated_template if current_user.is_authenticated else unauthenticated_template
        context = SimpleContext()
        error_message = f"Failed to render {template}"

        return render_safely(template, context, error_message, endpoint_name=endpoint)

    # Set function name for better debugging
    route_handler.__name__ = endpoint

    # Register the route
    blueprint.add_url_rule(
        url,
        endpoint=endpoint,
        view_func=route_handler,
        methods=methods
    )

    logger.info(f"Registered auth conditional route '{endpoint}' at '{url}'")

    return blueprint


def create_create_route(table_name, template_override=None):
    """Create a standard create form route function. (Legacy support)"""
    logger.warning("create_create_route is deprecated. Use register_page_route instead.")

    def create():
        """Create entity form."""
        context = SimpleContext(action="Create", table_name=table_name)
        template = template_override or "pages/crud/create.html"
        return render_safely(template, context, f"Failed to load create {table_name.lower()} form.")

    # Set the function name and docstring for better debugging
    create.__name__ = f"{table_name.lower()}_create"
    create.__doc__ = f"Create {table_name.lower()} form."

    return create


def create_view_route(table_name, service=None, template_override=None):
    """Create a standard view route function. (Legacy support)"""
    logger.warning("create_view_route is deprecated. Use register_page_route instead.")

    def view(item_id):
        """View entity details."""
        if service:
            # Get entity directly using the service
            item = service.get_by_id(item_id)

            if not item:
                flash(f"{table_name} not found.", "danger")
                return redirect(url_for(f"{table_name.lower()}s.index"))

            # Convert entity object to dictionary
            item_data = item.to_dict()

            context = SimpleContext(
                action="View",
                table_name=table_name,
                item=item_data
            )
        else:
            context = SimpleContext(action="View", table_name=table_name)

        template = template_override or "pages/crud/view.html"
        return render_safely(template, context, f"Failed to load {table_name.lower()} details.")

    # Set the function name and docstring for better debugging
    view.__name__ = f"{table_name.lower()}_view"
    view.__doc__ = f"View {table_name.lower()} details."

    return view


def create_edit_route(table_name, template_override=None):
    """Create a standard edit route function. (Legacy support)"""
    logger.warning("create_edit_route is deprecated. Use register_page_route instead.")

    def edit(item_id):
        """Edit entity form."""
        context = SimpleContext(action="Edit", table_name=table_name)
        template = template_override or "pages/crud/edit.html"
        return render_safely(template, context, f"Failed to load edit {table_name.lower()} form.")

    # Set the function name and docstring for better debugging
    edit.__name__ = f"{table_name.lower()}_edit"
    edit.__doc__ = f"Edit {table_name.lower()} form."

    return edit


def register_route(blueprint, route_type, table_name, service=None, template_override=None, url=None):
    """Register a single route on a blueprint. (Legacy support)"""
    logger.warning("register_route is deprecated. Use register_page_route instead.")

    # Handle special auth routes first
    if route_type == 'login':
        # Register login route with the explicit endpoint name "login"
        blueprint.route("/login", methods=["GET", "POST"], endpoint="login")(service.handle_login)
        logger.info(f"Registered 'login' route with endpoint '{blueprint.name}.login'")
        return
    elif route_type == 'logout':
        # Register logout route with the explicit endpoint name "logout"
        blueprint.route("/logout", endpoint="logout")(service.handle_logout)
        logger.info(f"Registered 'logout' route with endpoint '{blueprint.name}.logout'")
        return

    # Standard CRUD routes
    route_creators = {
        'index': create_index_route,
        'create': create_create_route,
        'view': create_view_route,
        'edit': create_edit_route
    }

    # Default URL patterns
    url_patterns = {
        'index': '/',
        'create': '/create',
        'view': '/<int:item_id>',
        'edit': '/<int:item_id>/edit'
    }

    # Create the route function
    if route_type not in route_creators:
        raise ValueError(f"Unsupported route type: {route_type}")

    if route_type == 'view':
        route_func = route_creators[route_type](table_name, service, template_override)
    else:
        route_func = route_creators[route_type](table_name, template_override)

    # Register the route with the blueprint
    blueprint.add_url_rule(
        url or url_patterns[route_type],
        endpoint=route_type,
        view_func=route_func
    )

    logger.info(f"Registered '{route_type}' route for '{table_name}'")


def register_blueprint_routes(blueprint, table_name, include_routes=None, service=None,
                              template_overrides=None, auth_templates=None):
    """Register a set of standard routes on a blueprint. (Legacy support)"""
    logger.warning("register_blueprint_routes is deprecated. Use register_crud_routes instead.")

    # Default routes if none specified
    if include_routes is None:
        include_routes = ['index', 'create', 'view', 'edit']

    # Default empty dict for template overrides
    if template_overrides is None:
        template_overrides = {}

    # Default empty dict for auth templates
    if auth_templates is None:
        auth_templates = {}

    logger.info(f"Registering {len(include_routes)} routes for {table_name} on {blueprint.name} blueprint")

    # Register each specified route
    for route_type in include_routes:
        try:
            template_override = template_overrides.get(route_type)
            auth_template_pair = auth_templates.get(route_type)

            # For auth-conditional templates
            if auth_template_pair:
                register_auth_conditional_route(
                    blueprint,
                    "/" if route_type == "index" else f"/{route_type}",
                    auth_template_pair.get('authenticated'),
                    auth_template_pair.get('unauthenticated'),
                    route_type
                )
            # For auth-specific routes we need to pass the service
            elif route_type in ['login', 'logout']:
                if service is None:
                    logger.error(f"Cannot register {route_type} route without a service")
                    continue
                register_route(blueprint, route_type, table_name, service=service,
                               template_override=template_override)
            else:
                # Standard CRUD routes
                register_route(blueprint, route_type, table_name, service=service,
                               template_override=template_override)

            logger.info(f"Successfully registered {route_type} route for {table_name}")
        except Exception as e:
            logger.error(f"Failed to register {route_type} route for {table_name}: {str(e)}")

    logger.info(f"Completed registration of routes for {table_name}")
    return blueprint