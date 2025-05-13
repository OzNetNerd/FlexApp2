# app/routes/api/pages/srs/review.py

from flask import jsonify, request
from app.services.srs import SRSService
from app.routes.api.pages.srs import srs_api_bp

# Initialize service
srs_service = SRSService()


@srs_api_bp.route("/due", methods=["GET"])
def get_due_items():
    """Return all SRS items due for review."""
    items = srs_service.get_due_items()
    return {"due": [i.to_dict() for i in items]}


@srs_api_bp.route("/<int:item_id>/preview", methods=["GET"])
def preview_item_ratings(item_id):
    """Show how long this card would be buried for each rating (0–5)."""
    return srs_service.preview_ratings(item_id)


@srs_api_bp.route("/<int:item_id>/review", methods=["POST"])
def review_item(item_id):
    """Submit a rating (0–5) and update the SRS schedule for that item."""
    data = request.get_json() or {}
    rating = int(data.get("rating", 0))
    item = srs_service.schedule_review(item_id, rating)
    return item.to_dict()
