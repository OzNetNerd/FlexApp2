import logging
from typing import Any, Dict

from flask import request, flash, redirect, url_for

from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import ResourceContext

logger = logging.getLogger(__name__)


def edit_route(ctx: Any, item_id: int) -> Any:
    """
    Handle requests for editing an existing item by its ID.

    Logs the edit request, retrieves the item, validates the form if it's a POST request,
    and either processes the edit or renders the edit form.

    Args:
        ctx (Any): The class instance containing dependencies.
        item_id (int): The ID of the item to edit.

    Returns:
        Any: The response from handling the edit operation.
    """
    ctx.request_logger.log_request_info(ctx.model.__name__, "edit", item_id)
    item, error = ctx.item_manager.get_item_by_id(item_id)
    if error or item is None:
        flash("Item not found.", "error")
        return redirect(url_for(f"{ctx.blueprint.name}.index"))
    if request.method == "POST":
        return handle_edit_form_submission(ctx, item)
    return render_edit_form(ctx, item)


def render_edit_form(ctx: Any, item: Any) -> Any:
    """
    Render the form template for editing an existing item.

    Converts the item to a dictionary, prepares context, and renders the edit form.

    Args:
        ctx (Any): The class instance containing model and template config.
        item (Any): The model instance to be edited.

    Returns:
        Any: The rendered edit form.
    """
    item_dict: Dict[str, Any] = item.to_dict()

    context = ResourceContext(
        model=ctx.model,
        blueprint_name=ctx.blueprint.name,
        item_dict=item_dict,
        item=None,
        title="Edit",
        read_only=False
    )

    return render_safely(ctx.edit_template, context, f"Error rendering edit form for {ctx.model.__name__}")


def handle_edit_form_submission(ctx: Any, item: Any) -> Any:
    """
    Process the submitted form data for editing an existing item.

    Validates and processes the form data, updates the item, logs changes, and flashes messages.

    Args:
        ctx (Any): The class instance containing entity handler and item manager.
        item (Any): The model instance being edited.

    Returns:
        Any: The updated item or a rendered edit form with error messages.
    """
    errors = ctx.entity_handler.validate_edit(item, request)
    if errors:
        for e in errors:
            flash(e, "error")
        return render_edit_form(ctx, item)

    logger.info(f"Raw form data received for edit (item ID {item.id}): {request.form.to_dict(flat=False)}")
    form_data = ctx._preprocess_form_data(request)
    logger.info(f"Processed submitted data for edit (item ID {item.id}): {form_data}")

    result, error = ctx.item_manager.update_item(item, form_data)
    if error:
        flash(error, "error")
        return render_edit_form(ctx, item)

    if hasattr(result, "to_dict"):
        logger.info(f"Database entry updated: {result.to_dict()}")
    else:
        logger.info(f"Database entry updated: {result}")
    flash(f"{ctx.model.__name__} updated successfully", "success")
    return result
