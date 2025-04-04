import logging
from datetime import datetime
from typing import Any, Dict, List

from flask import Request
from app.services.relationship_service import RelationshipService
from app.routes.base.components.autocomplete import get_autocomplete_field

logger = logging.getLogger(__name__)


def preprocess_form_data(ctx: Any, request: Request) -> Dict[str, Any]:
    """
    Process and transform form data from the request.

    Converts form data to a dictionary, casts date strings to datetime objects,
    and processes multi-select fields (for 'users' and 'companies') by filtering out empty strings.

    Args:
        ctx (Any): The class instance, used only for logging.
        request (Request): The incoming Flask request object.

    Returns:
        Dict[str, Any]: The processed form data.
    """
    raw_data: Dict[str, List[str]] = request.form.to_dict(flat=False)
    logger.info(f"Raw form data (flat=False): {raw_data}")

    form_data: Dict[str, Any] = request.form.to_dict()

    if "users" in request.form:
        users_list: List[str] = request.form.getlist("users")
        form_data["users"] = [u for u in users_list if u]
    if "companies" in request.form:
        companies_list: List[str] = request.form.getlist("companies")
        form_data["companies"] = [c for c in companies_list if c]

    if "created_at" in form_data and form_data["created_at"]:
        try:
            form_data["created_at"] = datetime.fromisoformat(form_data["created_at"])
        except ValueError:
            logger.error("Invalid format for created_at. Expected ISO format.")

    if "updated_at" in form_data and form_data["updated_at"]:
        try:
            form_data["updated_at"] = datetime.fromisoformat(form_data["updated_at"])
        except ValueError:
            logger.error("Invalid format for updated_at. Expected ISO format.")

    return form_data


def add_context(ctx: Any, item: Any, context: Dict[str, Any], edit_mode: bool) -> None:
    """
    Add additional context to the template rendering context, including relationships and autocomplete fields.

    For User models, adds autocomplete fields based on related relationships.

    Args:
        ctx (Any): The class instance with access to the model.
        item (Any): The item instance for which context is being added.
        context (Dict[str, Any]): The current context dictionary to update.
        edit_mode (bool): Flag indicating whether the context is for edit mode.
    """
    logger.debug(f"Adding relationships to the context for {ctx.model.__name__} {item.id}.")
    relationships = RelationshipService.get_relationships_for_entity("user", item.id)
    logger.info(f"Retrieved {len(relationships)} relationships for user with ID {item.id}.")
    logger.debug(f"Payload: {relationships}")

    if ctx.model.__name__ == "User":
        context["autocomplete_fields"] = [
            get_autocomplete_field("Users", relationships=relationships),
            get_autocomplete_field("Companies", relationships=relationships),
        ]

    logger.debug(f"Added {len(context.get('autocomplete_fields', []))} autocomplete fields to the {edit_mode} context.")


def get_item_display_name(item: Any) -> str:
    """
    Retrieve a user-friendly display name for a given item.

    Args:
        item (Any): The item instance.

    Returns:
        str: A user-friendly display name for the item.
    """
    for attr in ["name", "title", "email", "username"]:
        if hasattr(item, attr) and getattr(item, attr):
            return getattr(item, attr)
    if hasattr(item, "first_name") and hasattr(item, "last_name"):
        return f"{item.first_name} {item.last_name}".strip()
    return str(item.id)
