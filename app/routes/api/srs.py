from typing import Any, Dict
from flask import Blueprint, request, jsonify

from app.routes.api.route_registration import ApiCrudRouteConfig
from app.utils.app_logging import get_logger
from app.services.srs_service import SRSService, DEFAULT_EASE_FACTOR

logger = get_logger()

ENTITY_NAME = "SRS"
ENTITY_PLURAL_NAME = ENTITY_NAME

srs_api_bp = Blueprint(f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

srs_service = SRSService()

# Create config
srs_api_crud_config = ApiCrudRouteConfig(blueprint=srs_api_bp, entity_table_name=ENTITY_NAME, service=srs_service)


@srs_api_bp.route("/due", methods=["GET"])
def get_due_items():
    """Return all SRS items due for review."""
    items = srs_service.get_due_items()
    return {"due": [i.to_dict() for i in items]}


@srs_api_bp.route("/<int:item_id>/preview", methods=["GET"])
def preview_item_ratings(item_id: int) -> Dict[str, Any]:
    """Show how long this card would be buried for each rating (0–5)."""
    return srs_service.preview_ratings(item_id)


@srs_api_bp.route("/<int:item_id>/review", methods=["POST"])
def review_item(item_id: int) -> Dict[str, Any]:
    """Submit a rating (0–5) and update the SRS schedule for that item."""
    data = request.get_json() or {}
    rating = int(data.get("rating", 0))
    item = srs_service.schedule_review(item_id, rating)
    return item.to_dict()


@srs_api_bp.route("/stats", methods=["GET"])
def get_srs_stats():
    """Get current SRS system statistics."""
    return srs_service.get_stats()


@srs_api_bp.route("/categories", methods=["POST"])
def create_category_api():
    """API endpoint to add a new category."""
    data = request.get_json() or {}
    name = data.get("name")
    color = data.get("color", "#0d6efd")
    icon = data.get("icon", "folder")

    if not name:
        return {"error": "Category name is required"}, 400

    category = srs_service.create_category(name, color, icon)

    return {"id": name, "name": name, "color": color, "icon": icon}, 201


@srs_api_bp.route("/categories", methods=["GET"])
def get_categories_api():
    """API endpoint to get all categories."""
    categories = srs_service.get_categories()
    return {"categories": categories}


# API endpoint for chart data
@srs_api_bp.route("/progress-data", methods=["GET"])
def progress_data():
    """Get progress data for charts."""
    months = request.args.get("months", 7, type=int)
    data = srs_service.get_learning_progress_data(months=months)
    return jsonify(data)
