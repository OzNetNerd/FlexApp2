# app/routes/api/search.py

from flask import Blueprint, request, abort
from app.utils.app_logging import get_logger
from app.services.search_service import SearchService
from app.models import Company, Contact, Note, Opportunity, Task, User, SRSItem

logger = get_logger()

search_bp = Blueprint("search_bp", __name__, url_prefix="/api/search")

# Configure which fields to text-search for each entity
_entity_search_map = {
    "companies": (Company, ["name", "industry"]),
    "contacts":  (Contact, ["first_name", "last_name", "email"]),
    "notes":     (Note, ["content"]),
    "opportunities": (Opportunity, ["title", "status"]),
    "tasks":     (Task, ["title", "description"]),
    "users":     (User, ["username", "email"]),
    "srs":       (SRSItem, ["question", "answer"]),
}

# Instantiate one SearchService per entity
_search_services = {
    key: SearchService(model, fields)
    for key, (model, fields) in _entity_search_map.items()
}

@search_bp.route("/<entity_name>", methods=["GET"])
def search_entity(entity_name: str):
    """
    Generic search endpoint.
    Query params:
      - q: text term (optional)
      - any other: exact-match filters
    """
    svc = _search_services.get(entity_name)
    if not svc:
        logger.warning(f"Search for unknown entity '{entity_name}'")
        abort(404, f"No search available for '{entity_name}'")

    # extract term and exact filters
    params = request.args.to_dict(flat=True)
    term = params.pop("q", "")
    filters = {k: v for k, v in params.items() if v != ""}

    items = svc.search(term, filters)
    return {"data": [item.to_dict() for item in items]}
