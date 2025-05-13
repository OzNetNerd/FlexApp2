# app/routes/api/pages/srs/crud.py

from flask import jsonify, request
from app.models import SRS  # Assuming SRS model exists
from app.services.crud_service import CRUDService
from app.services.srs import SRSService
from app.routes.api.pages.srs import srs_api_bp
from app.routes.api.route_registration import ApiCrudRouteConfig
from app.utils.app_logging import get_logger

logger = get_logger()

# Register CRUD service and config
srs_crud_service = CRUDService(SRS)
srs_service = SRSService()
srs_api_crud_config = ApiCrudRouteConfig(blueprint=srs_api_bp, entity_table_name="SRS", service=srs_crud_service)


@srs_api_bp.route("/", methods=["GET"])
def get_all():
    """Get all SRS items."""
    items = srs_crud_service.get_all()
    return jsonify([item.to_dict() for item in items])


@srs_api_bp.route("/<int:item_id>", methods=["GET"])
def get(item_id):
    """Get an SRS item by ID."""
    item = srs_crud_service.get_by_id(item_id)
    if not item:
        return jsonify({"error": "SRS item not found"}), 404
    return jsonify(item.to_dict())


@srs_api_bp.route("/<int:item_id>", methods=["PATCH"])
def update_item_field(item_id):
    """Update a single field of an SRS item."""
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No update data provided"}), 400

        logger.info(f"Updating item {item_id} with data: {data}")

        # Get current item to validate it exists
        item = srs_crud_service.get_by_id(item_id)
        if not item:
            return jsonify({"error": f"Item with ID {item_id} not found"}), 404

        # Update only provided fields
        updated_item = srs_crud_service.update(item_id, data)
        return jsonify(updated_item.to_dict())
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {str(e)}")
        return jsonify({"error": f"Failed to update: {str(e)}"}), 500
