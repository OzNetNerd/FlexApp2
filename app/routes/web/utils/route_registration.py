# app/routes/web/route_registration.py - Improved with better structure

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar

from flask import Blueprint, redirect, request, url_for, Response
from flask_login import login_required
from markupsafe import Markup

from app.routes.web.utils.template_renderer import RenderSafelyConfig, render_safely
from app.routes.web.utils.context import TableContext, WebContext
from app.utils.app_logging import get_logger
from app.routes.web.utils.template_config import TemplateConfig

logger = get_logger()

# Type aliases
ContextType = TypeVar('ContextType', bound=Union[TableContext, WebContext])
EntityType = TypeVar('EntityType')


class CRUDEndpoint(Enum):
    index = "index"
    create = "create"
    view = "view"
    edit = "edit"
    delete = "delete"

    @classmethod
    def is_valid(cls, name: str) -> bool:
        """Check if a string is a valid CRUD endpoint.

        Args:
            name: The string to check against CRUD endpoint values

        Returns:
            bool: True if the name is a valid CRUD endpoint, False otherwise
        """
        return name in cls._value2member_map_


@dataclass
class CrudRouteConfig:
    blueprint: Blueprint
    entity_table_name: str
    service: Any
    model_class: Any
    template_config: TemplateConfig
    form_class: Optional[Any] = None

    def get_template(self, route_type: str, default: str) -> str:
        """Get the template path for a specific route type.

        Args:
            route_type: The CRUD endpoint type
            default: Default template path to use if not configured

        Returns:
            str: Template path to use for rendering
        """
        return self.template_config.get_template(route_type, default)


def handle_crud_operation(
        endpoint: str,
        service: Any,
        blueprint_name: str,
        entity_id: Optional[int],
        form_data: Dict[str, Any]
) -> Optional[Response]:
    """Handle CRUD operations for POST requests.

    Args:
        endpoint: The CRUD endpoint type (create, edit, delete)
        service: The service to use for data operations
        blueprint_name: The blueprint name for URL generation
        entity_id: The ID of the entity (for edit/delete operations)
        form_data: Form data submitted with the request

    Returns:
        Optional[Response]: A redirect response if the operation was successful, None otherwise
    """
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


def load_entity(
        endpoint: str,
        service: Any,
        entity_id: Optional[int]
) -> Optional[Any]:
    """Load an entity from the database for view/edit operations.

    Args:
        endpoint: The CRUD endpoint type
        service: The service to use for data operations
        entity_id: The ID of the entity to load

    Returns:
        Optional[Any]: The loaded entity or None if not applicable
    """
    if endpoint in (CRUDEndpoint.view.value, CRUDEndpoint.edit.value) and entity_id:
        entity = service.get_by_id(entity_id)
        logger.info(f"Loaded entity for {endpoint}: ID={entity_id}, entity={entity}")
        return entity
    return None


def build_index_context(config: CrudRouteConfig) -> TableContext:
    """Build context for index endpoint.

    Args:
        config: The CRUD route configuration

    Returns:
        TableContext: The context for rendering the index template
    """
    return TableContext(entity_table_name=config.entity_table_name)


def build_create_context(config: CrudRouteConfig, form=None) -> TableContext:
    """Build context for create endpoint.

    Args:
        config: The CRUD route configuration

    Returns:
        TableContext: The context for rendering the create template
    """
    context = TableContext(
        entity={},
        entity_table_name=config.entity_table_name,
        action="create",
        read_only=False,
        title=f"Create {config.entity_table_name}",
        submit_url=url_for(f"{config.blueprint.name}.create")
    )

    if form:
        context.form = form

    return context


def build_view_edit_context(
        config: CrudRouteConfig,
        endpoint: str,
        entity: Any,
        entity_id: int,
        form=None,
) -> TableContext:
    """Build context for view/edit endpoints.

    Args:
        config: The CRUD route configuration
        endpoint: The CRUD endpoint type (view or edit)
        entity: The entity to view or edit
        entity_id: The ID of the entity

    Returns:
        TableContext: The context for rendering the view/edit template
    """
    read_only = endpoint == CRUDEndpoint.view.value
    title = f"{'View' if read_only else 'Edit'} {config.entity_table_name}"

    context = TableContext(
        entity=entity,
        entity_table_name=config.entity_table_name,
        action=endpoint,
        entity_id=entity_id,
        read_only=read_only,
        title=title
    )

    # Add form to context if available
    if form:
        context.form = form

    # Add other context variables...
    context.id = entity_id
    context.model_name = config.model_class.__name__

    # Get entity name for display
    if hasattr(entity, "name"):
        context.entity_name = entity.name
    elif hasattr(entity, "title"):
        context.entity_name = entity.title
    else:
        context.entity_name = f"{config.model_class.__name__} #{entity_id}"

    # Set submit URL
    if endpoint == CRUDEndpoint.edit.value:
        context.submit_url = url_for(f"{config.blueprint.name}.update", entity_id=entity_id)

    return context


def add_csrf_to_context(context: ContextType) -> ContextType:
    """Add CSRF token to the context if available.

    Args:
        context: The context object to add CSRF token to

    Returns:
        ContextType: The context object with CSRF token added
    """
    try:
        from flask_wtf.csrf import generate_csrf

        context.csrf_token = generate_csrf()
        context.csrf_input = Markup(f'<input type="hidden" name="csrf_token" value="{generate_csrf()}">')
    except ImportError:
        context.csrf_token = ""
        context.csrf_input = ""

    return context


def route_handler(endpoint: str, config: CrudRouteConfig) -> Callable:
    """Create a route handler function for CRUD operations.

    This function generates a handler for Flask routes that handles CRUD operations.
    It processes form submissions, loads entities, builds appropriate context objects,
    and renders templates with the correct data.

    Args:
        endpoint: The CRUD endpoint type (index, create, view, edit, delete)
        config: The configuration for CRUD routes

    Returns:
        Callable: A Flask view function that handles requests for the specified endpoint
    """

    def handler(*args: Any, **kwargs: Any) -> Any:
        """Handle CRUD route requests.

        Args:
            *args: Positional arguments from the route
            **kwargs: Keyword arguments from the route

        Returns:
            Any: The response to the request
        """
        logger.info(f"Handling {request.method} {endpoint} with args={args}, kwargs={kwargs}")

        entity_id = kwargs.get("entity_id")
        entity = load_entity(endpoint, config.service, entity_id)
        form = None

        # Create form if form_class is provided
        if config.form_class:
            if endpoint in (CRUDEndpoint.edit.value, CRUDEndpoint.view.value) and entity:
                form = config.form_class(obj=entity)
            else:
                form = config.form_class()

            # Process form on POST
            if request.method == "POST":
                form = config.form_class(formdata=request.form, obj=entity)
                if form.validate():
                    if endpoint == CRUDEndpoint.create.value:
                        # Create new entity from form
                        new_entity = config.model_class()
                        form.populate_obj(new_entity)
                        created_entity = config.service.create(new_entity)
                        return redirect(url_for(f"{config.blueprint.name}.view", entity_id=created_entity.id))
                    elif endpoint == CRUDEndpoint.edit.value:
                        # Update existing entity from form
                        form.populate_obj(entity)
                        updated_entity = config.service.update(entity)
                        return redirect(url_for(f"{config.blueprint.name}.view", entity_id=updated_entity.id))
        elif request.method == "POST" and CRUDEndpoint.is_valid(endpoint):
            # Fall back to existing behavior if no form_class
            result = handle_crud_operation(
                endpoint,
                config.service,
                config.blueprint.name,
                entity_id,
                request.form.to_dict(),
            )
            if result:
                return result

        # Handle DELETE requests
        if endpoint == CRUDEndpoint.delete.value and request.method == "POST":
            config.service.delete(entity_id)
            return redirect(url_for(f"{config.blueprint.name}.index"))

        # Build context with form
        if endpoint == CRUDEndpoint.index.value:
            context = build_index_context(config)
        elif endpoint == CRUDEndpoint.create.value:
            context = build_create_context(config, form)
        elif endpoint in (CRUDEndpoint.view.value, CRUDEndpoint.edit.value):
            context = build_view_edit_context(
                config,
                endpoint,
                entity,
                entity_id,
                form
            )
        else:
            context = WebContext(title=config.entity_table_name)

        # Add form to context if available
        if form:
            context.form = form

        # Add CSRF token
        context = add_csrf_to_context(context)

        # Render template
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


def register_crud_routes(config: CrudRouteConfig) -> None:
    """Register CRUD routes with a Flask blueprint.

    Args:
        config: The configuration for CRUD routes
    """
    bp = config.blueprint
    bp.add_url_rule(rule="/create", endpoint="create", view_func=route_handler("create", config),
                    methods=["GET", "POST"])
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


def register_auth_route(
        blueprint: Blueprint,
        url: str,
        handler: Callable,
        endpoint_name: str,
        methods: Optional[List[str]] = None
) -> None:
    """Register an authentication route with a Flask blueprint.

    Args:
        blueprint: The Flask blueprint to register the route with
        url: The URL rule for the route
        handler: The view function to handle requests
        endpoint_name: The name of the endpoint
        methods: HTTP methods allowed for this route (defaults to ["GET"])
    """
    methods = methods or ["GET"]
    blueprint.add_url_rule(rule=url, endpoint=endpoint_name, view_func=handler, methods=methods)