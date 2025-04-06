import logging
from flask import jsonify, request
from app.routes.blueprint_factory import create_blueprint
from app.models import Opportunity
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)

# Create API blueprint with /api prefix for opportunities
opportunities_api_bp = create_blueprint("api_opportunities", url_prefix="/api/opportunities")
opportunity_service = CRUDService(Opportunity)

@opportunities_api_bp.route("/", methods=["GET"])
def get_all_opportunities():
    """Get all opportunities."""
    opportunities = opportunity_service.get_all()
    return jsonify([opportunity.to_dict() for opportunity in opportunities])

@opportunities_api_bp.route("/<int:item_id>", methods=["GET"])
def get_opportunity(item_id):
    """Get a specific opportunity."""
    opportunity = opportunity_service.get_by_id(item_id)
    if not opportunity:
        return jsonify({"error": "Opportunity not found"}), 404
    return jsonify(opportunity.to_dict())

@opportunities_api_bp.route("/", methods=["POST"])
def create_opportunity():
    """Create a new opportunity."""
    data = request.get_json()
    result = opportunity_service.create(data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201

@opportunities_api_bp.route("/<int:item_id>", methods=["PUT"])
def update_opportunity(item_id):
    """Update an opportunity."""
    data = request.get_json()
    result = opportunity_service.update(item_id, data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@opportunities_api_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_opportunity(item_id):
    """Delete an opportunity."""
    result = opportunity_service.delete(item_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

logger.info("Opportunities API routes instantiated successfully.")
