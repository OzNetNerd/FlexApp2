import logging
from typing import Any, Dict

from flask import request, flash

from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import ResourceContext

logger = logging.getLogger(__name__)


def create_route(ctx: Any) -> Any:
    """
    Handle requests for creating a new item.

    For POST requests, process the form submission; for GET requests, render the create form.

    Args:
        ctx (Any): The class instance containing request_logger, model, etc.

    Returns:
        Any: The response from handling the create operation.
    """
    ctx.request_logger.log_request_info(ctx.model.__name__, "create")
    if request.method == "POST":
        return handle_create_form_submission(ctx)
    return render_create_form(ctx)


def render_create_form(ctx: Any) -> Any:
    """
    Render the form template for creating a new item.

    Prepares the context (including tabs and title) and safely renders the create form template.

    Args:
        ctx (Any): The class instance containing model, blueprint, etc.

    Returns:
        Any: The rendered create form.
    """
    item_dict: Dict[str, Any] = {}

    context = ResourceContext(
        model=ctx.model, blueprint_name=ctx.blueprint.name, item_dict=item_dict, title=f"Create a {ctx.model.__name__}", read_only=False
    )
    return render_safely(ctx.create_template, context, f"Error rendering create form for {ctx.model.__name__}")


def handle_create_form_submission(ctx: Any) -> Any:
    """
    Process the submitted form data for creating a new item.

    Validates the form data, processes the submitted information, creates the item,
    logs the creation, and flashes a success message upon completion.

    Args:
        ctx (Any): The class instance containing entity_handler, item_manager, etc.

    Returns:
        Any: The created item or a rendered create form with error messages.
    """
    errors = ctx.entity_handler.validate_create(request)
    if errors:
        for e in errors:
            flash(e, "error")
        return render_create_form(ctx)

    logger.info(f"Raw form data received for create: {request.form.to_dict(flat=False)}")
    form_data = ctx._preprocess_form_data(request)  # assuming method still on main class
    logger.info(f"Processed submitted data for create: {form_data}")

    result, error = ctx.item_manager.create_item(form_data)
    if error:
        flash(error, "error")
        return render_create_form(ctx)

    if hasattr(result, "to_dict"):
        logger.info(f"Database entry created: {result.to_dict()}")
    else:
        logger.info(f"Database entry created: {result}")
    flash(f"{ctx.model.__name__} created successfully", "success")
    return result
