# app/routes/api/srs.py (Updated)

import logging
from flask import Blueprint, jsonify, request

from app.services.srs_service import SRSService
from app.models.srs_item import SRSItem
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig

logger = logging.getLogger(__name__)

ENTITY_NAME = "SRSItem"
ENTITY_PLURAL_NAME = "SRS"

srs_api_bp = Blueprint(f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")
srs_service = SRSService()

# Register all standard CRUD API routes
srs_api_crud_config = ApiCrudRouteConfig(blueprint=srs_api_bp, entity_table_name=ENTITY_NAME, service=srs_service)
register_api_crud_routes(srs_api_crud_config)


# Add custom endpoints for SRS-specific functionality
@srs_api_bp.route("/due", methods=["GET"])
def get_due_items():
    """Get all items due for review."""
    items = srs_service.get_due_items()
    return jsonify([item.to_dict() for item in items])


@srs_api_bp.route("/<int:item_id>/preview", methods=["GET"])
def preview_item_ratings(item_id):
    """Preview the next review intervals for each possible rating."""
    try:
        preview_data = srs_service.preview_ratings(item_id)
        # Format the data for display
        formatted_data = {
            rating: f"{days} days" if days != 1 else "1 day"
            for rating, days in preview_data.items()
        }
        return jsonify({
            "success": True,
            "intervals": formatted_data
        })
    except Exception as e:
        logger.error(f"Error previewing ratings for item {item_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@srs_api_bp.route("/<int:item_id>/review", methods=["POST"])
def review_item(item_id):
    """Process a review for an SRS item."""
    data = request.get_json()
    if not data or "rating" not in data:
        return jsonify({"success": False, "error": "Missing rating parameter"}), 400

    try:
        # Get the rating from the request
        rating = int(data["rating"])

        # The FSRS library only accepts ratings 0-4, but our UI goes to 5
        # Map rating 5 to 4 if needed
        fsrs_rating = min(rating, 4)

        # Pass the adjusted rating to the service
        item = srs_service.schedule_review(item_id, fsrs_rating)

        return jsonify({
            "success": True,
            "item": item.to_dict(),
            "next_review_at": item.next_review_at.isoformat()
        })
    except Exception as e:
        logger.error(f"Error processing review for item {item_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@srs_api_bp.route("/items", methods=["GET"])
def get_all_items():
    """Get all SRS items."""
    items = SRSItem.query.all()
    return jsonify([item.to_dict() for item in items])