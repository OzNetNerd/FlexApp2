# api/notes.py

import logging
from flask import Blueprint, request, jsonify
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig
from app.routes.api.route_registration import json_response, ErrorAPIContext, ListAPIContext
from app.models import Note
from app.services.note_service import NoteService

logger = logging.getLogger(__name__)

ENTITY_NAME = "Note"
ENTITY_PLURAL_NAME = "Notes"

notes_api_bp = Blueprint(f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")
note_service = NoteService()

# Register all standard CRUD API routes
note_api_crud_config = ApiCrudRouteConfig(
    blueprint=notes_api_bp,
    entity_table_name=ENTITY_NAME,
    service=note_service
)
register_api_crud_routes(note_api_crud_config)


# Additional route for getting notes by notable entity
@notes_api_bp.route("/by-notable/<string:notable_type>/<int:notable_id>", methods=["GET"])
def get_notes_by_notable(notable_type, notable_id):
    """Get all notes related to a specific entity."""
    try:
        notes = note_service.get_by_notable(notable_type, notable_id)

        return json_response(
            ListAPIContext(
                entity_table_name=ENTITY_NAME,
                items=notes,
                total_count=len(notes)
            )
        )
    except Exception as e:
        logger.error(f"Error getting notes for {notable_type} {notable_id}: {e}", exc_info=True)
        return json_response(
            ErrorAPIContext(
                message=f"Error retrieving notes: {str(e)}",
                status_code=500
            )
        )


logger.info(f"{ENTITY_PLURAL_NAME} API routes registered successfully.")