# app/routes/base/web_utils.py
import logging
from flask import url_for, redirect, flash, Blueprint
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import SimpleContext
from typing import Optional, List, Any


logger = logging.getLogger(__name__)


def create_index_route(table_name=None, template_override=None):
    """Create a standard index route function for an entity.

    Args:
        table_name (str, optional): The name of the entity table
        template_override (str, optional): Custom template path if needed

    Returns:
        function: The route handler function
    """
    # Mapping for irregular plurals
    plural_mapping = {
        "company": "companies",
        "opportunity": "opportunities",
        "category": "categories",
        "capability": "capabilities",
    }

    def index():
        """Entity list page."""
        if table_name:
            # Determine the plural form
            table_name_lower = table_name.lower()
            plural_form = plural_mapping.get(table_name_lower, f"{table_name_lower}s")

            context = SimpleContext(title=f"{table_name}s", table_name=table_name)
            template = template_override or f"pages/tables/{plural_form}.html"
            return render_safely(template, context, f"Failed to load {plural_form}.")
        else:
            # Handle case when no table_name is provided
            context = SimpleContext(title="Items")
            template = template_override or "pages/tables/generic.html"
            return render_safely(template, context, "Failed to load items.")

    # Set the function name and docstring for better debugging
    if table_name:
        index.__name__ = f"{table_name.lower()}_index"
        index.__doc__ = f"{table_name}s list page."
    else:
        index.__name__ = "generic_index"
        index.__doc__ = "Generic list page."

    return index


def create_create_route(table_name, template_override=None):
    """Create a standard create form route function for an entity.

    Args:
        table_name (str): The name of the entity table
        template_override (str, optional): Custom template path if needed

    Returns:
        function: The route handler function
    """

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
    """Create a standard view route function for an entity.

    Args:
        table_name (str): The name of the entity table
        service (object, optional): Service with get_by_id method
        template_override (str, optional): Custom template path if needed

    Returns:
        function: The route handler function
    """

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
    """Create a standard edit route function for an entity.

    Args:
        table_name (str): The name of the entity table
        template_override (str, optional): Custom template path if needed

    Returns:
        function: The route handler function
    """

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
    """Register a single route on a blueprint.

    Args:
        blueprint (Blueprint): The Flask blueprint
        route_type (str): One of 'index', 'create', 'view', 'edit', 'login', 'logout'
        table_name (str): The name of the entity table
        service (object, optional): Service with get_by_id method
        template_override (str, optional): Custom template path if needed
        url (str, optional): Custom URL pattern
    """
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


def register_blueprint_routes(blueprint, table_name, routes=None, service=None, template_overrides=None):
    """Register a set of standard routes on a blueprint.

    Args:
        blueprint (Blueprint): The Flask blueprint
        table_name (str): The name of the entity table
        routes (list, optional): List of route types to register.
                                Defaults to ['index', 'create', 'view', 'edit'].
        service (object, optional): Service with appropriate methods
        template_overrides (dict, optional): Custom template paths for specific routes
    """
    # Default routes if none specified
    if routes is None:
        routes = ['index', 'create', 'view', 'edit']

    # Default empty dict for template overrides
    if template_overrides is None:
        template_overrides = {}

    logger.info(f"Registering {len(routes)} routes for {table_name} on {blueprint.name} blueprint")

    # Register each specified route
    for route_type in routes:
        try:
            template_override = template_overrides.get(route_type)

            # For auth-specific routes we need to pass the service
            if route_type in ['login', 'logout']:
                if service is None:
                    logger.error(f"Cannot register {route_type} route without a service")
                    continue

                register_route(
                    blueprint,
                    route_type,
                    table_name,
                    service=service,
                    template_override=template_override
                )
            else:
                # Standard CRUD routes
                register_route(
                    blueprint,
                    route_type,
                    table_name,
                    service=service,
                    template_override=template_override
                )

            logger.info(f"Successfully registered {route_type} route for {table_name}")
        except Exception as e:
            logger.error(f"Failed to register {route_type} route for {table_name}: {str(e)}")
            # Optionally re-raise the exception if you want it to bubble up
            # raise

    logger.info(f"Completed registration of routes for {table_name}")
    return blueprint