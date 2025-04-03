import logging
from typing import Any, Dict

from flask import request, flash, redirect, url_for

from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import ResourceContext
from app.services.relationship_service import RelationshipService

logger = logging.getLogger(__name__)


def view_route(ctx: Any, item_id: int) -> Any:
    """
    Handle requests to view an item by its ID.

    Logs the request, retrieves the item, optionally processes relationships,
    prepares the context, and renders the view template.

    Args:
        ctx (Any): The class instance containing request_logger, item_manager, model, blueprint, etc.
        item_id (int): The ID of the item to view.

    Returns:
        Any: The rendered view template or a redirect if errors occur.
    """
    ctx.request_logger.log_request_info(ctx.model.__name__, "view", item_id)
    item, error = ctx.item_manager.get_item_by_id(item_id)

    if error:
        flash(error, "error")
        return redirect(url_for(f"{ctx.blueprint.name}.index"))

    if request.method == "POST":
        return ctx._handle_view_post(item)  # assuming this is still on the class

    item_dict: Dict[str, Any] = item.to_dict()

    if ctx.model.__name__ == "User":
        relationships = RelationshipService.get_relationships_for_entity("user", item_id)
        item_dict["related_users"] = [rel for rel in relationships if rel["entity_type"] == "user"]
        item_dict["related_companies"] = [rel for rel in relationships if rel["entity_type"] == "company"]

    logger.info(f"This is item: {item_dict}")

    # Optional: inject relationships into tab sections here (commented for future use)
    # tabs = ctx.create_tabs_function()
    # if ctx.model.__name__ == "User":
    #     for tab in tabs:
    #         if tab.tab_name == "Mappings":
    #             for section in tab.sections:
    #                 for entry in section.entries:
    #                     if entry.entry_name == "users" and 'related_users' in item_dict:
    #                         entry.value = item_dict['related_users']
    #                     elif entry.entry_name == "companies" and 'related_companies' in item_dict:
    #                         entry.value = item_dict['related_companies']

    context = ResourceContext(
        model=ctx.model,
        blueprint_name=ctx.blueprint.name,
        item_dict=item_dict,
        item=None,
        title="Viewing",
        read_only=True
    )

    return render_safely(ctx.view_template, context, f"Error viewing {ctx.model.__name__} with id {item_id}")
