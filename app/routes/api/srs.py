import logging
from flask import Blueprint

from app.services.srs_service import SRSService

logger = logging.getLogger(__name__)

srs_api_bp = Blueprint("srs_api_bp", __name__, url_prefix="/srs")

srs_service = SRSService()

# For simplicity, expose only the “get due cards” and “submit review” endpoints:

@srs_api_bp.get("/due")
def get_due():
    items = srs_service.get_due_items()
    return {"due": [i.to_dict() for i in items]}

@srs_api_bp.post("/<int:item_id>/review")
def submit_review(item_id):
    data = Blueprint.current_request.get_json() or {}
    rating = int(data.get("rating", 0))
    updated = srs_service.schedule_review(item_id, rating)
    return updated.to_dict()
