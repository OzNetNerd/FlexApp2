# app/routes/api/srs.py

import logging
from flask import Blueprint, request, jsonify
from app.routes.api.route_registration import (
    register_api_crud_routes,
    ApiCrudRouteConfig,
    json_response,
    ErrorAPIContext,
    ListAPIContext,
)
from app.services.srs_service import SRSService

logger = logging.getLogger(__name__)

# Define entity names
ENTITY_NAME = "SRSItem"
ENTITY_PLURAL_NAME = "SRS"

# Blueprint setup
srs_api_bp = Blueprint(
    f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}"
)

# Service instance
srs_service = SRSService()

# Register standard CRUD index route
srs_api_crud_config = ApiCrudRouteConfig(
    blueprint=srs_api_bp,
    entity_table_name=ENTITY_NAME,
    service=srs_service,
)
register_api_crud_routes(srs_api_crud_config)

# Custom endpoints
@srs_api_bp.route("/due", methods=["GET"])
def get_due():
    try:
        items = srs_service.get_due_items()
        return json_response(
            ListAPIContext(
                entity_table_name=ENTITY_NAME,
                items=items,
                total_count=len(items),
            )
        )
    except Exception as e:
        logger.error(f"Error fetching due SRS cards: {e}", exc_info=True)
        return json_response(
            ErrorAPIContext(message=str(e), status_code=500)
        )

@srs_api_bp.route("/<int:entity_id>/review", methods=["POST"])
def submit_review(entity_id):
    try:
        data = request.get_json() or {}
        rating = int(data.get("rating", 0))
        updated = srs_service.schedule_review(entity_id, rating)
        return jsonify(updated.to_dict())
    except Exception as e:
        logger.error(f"Error scheduling review for item {entity_id}: {e}", exc_info=True)
        return json_response(
            ErrorAPIContext(message=str(e), status_code=500)
        )

logger.info(f"{ENTITY_PLURAL_NAME} API routes registered successfully.")