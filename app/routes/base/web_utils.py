# app/routes/base/web_utils.py
import logging
from flask import url_for, redirect, flash
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import SimpleContext


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
        route_type (str): One of 'index', 'create', 'view', 'edit'
        table_name (str): The name of the entity table
        service (object, optional): Service with get_by_id method
        template_override (str, optional): Custom template path if needed
        url (str, optional): Custom URL pattern
    """
    route_creators = {
        'index': create_index_route,
        'create': create_create_route,
        'view': create_view_route,
        'edit': create_edit_route
    }

    if route_type == 'login':
        blueprint.route("/login", methods=["GET", "POST"])(service.handle_login)
    elif route_type == 'logout':
        blueprint.route("/logout")(service.handle_logout)

    # Default URL patterns
    url_patterns = {
        'index': '/',
        'create': '/create',
        'view': '/<int:item_id>',
        'edit': '/<int:item_id>/edit'
    }

    # Create the route function
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


from flask import Blueprint
from typing import Optional, List, Any


def register_blueprint_routes(
        blueprint: Blueprint,
        table_name: str,
        routes: Optional[List[str]] = None,
        service: Optional[Any] = None
) -> None:
    """Register specified routes on a blueprint.

    This function adds multiple routes to a given blueprint based on the provided
    route types list. For each route type, it calls register_route to set up the
    appropriate handlers.

    Args:
        blueprint (Blueprint): The Flask blueprint to register routes on
        table_name (str): The name of the entity table (used for templates and logging)
        routes (Optional[List[str]]): List of route types to register
                                     e.g. ['index', 'create', 'view', 'edit']
                                     Defaults to all standard routes if None
        service (Optional[Any]): Service object with necessary handler methods

    Returns:
        None: This function modifies the blueprint in-place

    Example:
        register_blueprint_routes(companies_bp, "Company", service=company_service)
    """
    # Default to all standard routes if not specified
    if routes is None:
        routes = ['index', 'create', 'view', 'edit']

    for route_type in routes:
        register_route(blueprint, route_type, table_name, service)

    logger.info(f"Registered {len(routes)} routes for '{table_name}'")