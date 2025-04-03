import logging
from typing import Any

from flask import flash, redirect, url_for

logger = logging.getLogger(__name__)


def delete_route(ctx: Any, item_id: int) -> Any:
    """
    Handle the deletion of an item by its ID.

    Logs the deletion request, attempts to delete the item, flashes appropriate messages,
    and redirects to the index page.

    Args:
        ctx (Any): The class instance containing request_logger, model, item_manager, and blueprint.
        item_id (int): The ID of the item to delete.

    Returns:
        Any: The redirect response to the index page.
    """
    ctx.request_logger.log_request_info(ctx.model.__name__, "delete", item_id)
    item, error = ctx.item_manager.get_item_by_id(item_id)
    if error:
        flash(error, "error")
    else:
        success, error = ctx.item_manager.delete_item(item)
        if error:
            flash(error, "error")
        else:
            flash(f"{ctx.model.__name__} deleted successfully", "success")
    return redirect(url_for(f"{ctx.blueprint.name}.index"))
