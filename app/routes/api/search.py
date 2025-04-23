# app/routes/api/search.py

from flask import Blueprint, request, abort
from app.models.company import Company
from app.models.contact import Contact
from app.models.note import Note
from app.models.opportunity import Opportunity
from app.models.task import Task
from app.models.user import User
from app.models.srs_item import SRSItem

from app.services.search_service import SearchService
from app.utils.app_logging import get_logger
from .json_utils import json_endpoint

logger = get_logger()

search_bp = Blueprint("search_bp", __name__, url_prefix="/api/search")

# Map each entity name to its model and searchable fields
_entity_search_map = {
    "companies":     (Company, ["name", "industry"]),
    "contacts":      (Contact, ["first_name", "last_name", "email"]),
    "notes":         (Note, ["content"]),
    "opportunities": (Opportunity, ["title", "status"]),
    "tasks":         (Task, ["title", "description"]),
    "users":         (User, ["username", "email"]),
    "srs":           (SRSItem, ["question", "answer"]),
}

# Instantiate one SearchService per entity
_search_services = {
    key: SearchService(model, fields)
    for key, (model, fields) in _entity_search_map.items()
}

@search_bp.route("/<entity_name>", methods=["GET"])
@json_endpoint
def search_entity(entity_name: str):
    """
    Generic search endpoint.

    Query params:
      - q: text term (optional)
      - any other: exact-match filters
    """
    svc = _search_services.get(entity_name)
    if not svc:
        abort(404, f"No search available for '{entity_name}'")

    params = request.args.to_dict(flat=True)
    term = params.pop("q", "")
    filters = {k: v for k, v in params.items() if v != ""}

    items = svc.search(term, filters)
    # Return a list of plain dicts; json_endpoint will wrap it
    return [item.to_dict() for item in items]
