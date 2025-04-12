# api/notes.py

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig
from app.routes.api.route_registration import json_response, ErrorAPIContext, ListAPIContext
from app.models import Note
# Import CRUDService directly and initialize it here to avoid circular imports
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)

ENTITY_NAME = "Note"
ENTITY_PLURAL_NAME = "Notes"

notes_api_bp = Blueprint(f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

# Create service instance directly here instead of importing NoteService
note_service = CRUDService(Note)

# Register all standard CRUD API routes
note_api_crud_config = ApiCrudRouteConfig(
    blueprint=notes_api_bp,
    entity_table_name=ENTITY_NAME,
    service=note_service
)
register_api_crud_routes(note_api_crud_config)


# Single unified query endpoint for filtering notes
@notes_api_bp.route("/query", methods=["GET"])
def query_notes():
    """
    Query notes with combined filters.

    Supported query parameters:
    - notable_type: Type of entity (Company, Contact, etc.)
    - notable_id: ID of the entity
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - days: Get notes from the last X days
    - q: Search term for content
    - user_id: Filter by user ID
    - page: Page number (for pagination)
    - per_page: Items per page (for pagination)
    """
    try:
        # Initialize the query
        query = Note.query

        # Apply filters based on query parameters
        filters = []

        # Filter by notable entity
        notable_type = request.args.get("notable_type")
        notable_id = request.args.get("notable_id")
        if notable_type and notable_id:
            filters.append(and_(
                Note.notable_type == notable_type,
                Note.notable_id == int(notable_id)
            ))

        # Filter by date range
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                # Add a day to end_date to make it inclusive
                end = end + timedelta(days=1)
                filters.append(and_(
                    Note.created_at >= start,
                    Note.created_at < end
                ))
            except ValueError as e:
                return json_response(
                    ErrorAPIContext(
                        message=f"Invalid date format: {str(e)}",
                        status_code=400
                    )
                )

        # Filter by days ago
        days = request.args.get("days")
        if days and not (start_date or end_date):  # Only apply if date range not specified
            try:
                days_ago = int(days)
                if days_ago <= 0:
                    return json_response(
                        ErrorAPIContext(
                            message="Days parameter must be a positive integer",
                            status_code=400
                        )
                    )
                start_date = datetime.now() - timedelta(days=days_ago)
                filters.append(Note.created_at >= start_date)
            except ValueError:
                return json_response(
                    ErrorAPIContext(
                        message="Days parameter must be a valid integer",
                        status_code=400
                    )
                )

        # Filter by user ID
        user_id = request.args.get("user_id")
        if user_id:
            try:
                filters.append(Note.user_id == int(user_id))
            except ValueError:
                return json_response(
                    ErrorAPIContext(
                        message="User ID must be a valid integer",
                        status_code=400
                    )
                )

        # Search by content
        search_term = request.args.get("q")
        if search_term:
            search_pattern = f"%{search_term}%"
            filters.append(or_(
                Note.content.ilike(search_pattern),
                Note.processed_content.ilike(search_pattern)
            ))

        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))

        # Add default sorting
        query = query.order_by(Note.created_at.desc())

        # Handle pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 15, type=int)

        # Execute query with pagination
        paginated_notes = query.paginate(page=page, per_page=per_page, error_out=False)

        return json_response(
            ListAPIContext(
                entity_table_name=ENTITY_NAME,
                items=paginated_notes.items,
                total_count=paginated_notes.total,
                page=page,
                per_page=per_page
            )
        )

    except Exception as e:
        logger.error(f"Error querying notes: {e}", exc_info=True)
        return json_response(
            ErrorAPIContext(
                message=f"Error retrieving notes: {str(e)}",
                status_code=500
            )
        )


# Helper function for notes by notable type/id
def get_notes_by_notable_entity(notable_type, notable_id):
    """Get notes by notable entity type and ID."""
    try:
        return Note.query.filter_by(
            notable_type=notable_type,
            notable_id=notable_id
        ).order_by(Note.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Error getting notes for {notable_type} {notable_id}: {e}")
        raise


# Helper function for notes by content search
def search_notes_by_content(search_term):
    """Search notes by content."""
    try:
        search_pattern = f"%{search_term}%"
        return Note.query.filter(
            or_(
                Note.content.ilike(search_pattern),
                Note.processed_content.ilike(search_pattern)
            )
        ).order_by(Note.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Error searching notes: {e}")
        raise


@notes_api_bp.route("/filter/notable/<string:notable_type>/<int:notable_id>", methods=["GET"])
def get_notes_by_notable(notable_type, notable_id):
    """Get all notes related to a specific entity."""
    try:
        notes = get_notes_by_notable_entity(notable_type, notable_id)

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


@notes_api_bp.route("/search", methods=["GET"])
def search_notes():
    """Search notes by content."""
    try:
        search_term = request.args.get("q")

        if not search_term:
            return json_response(
                ErrorAPIContext(
                    message="Search query parameter 'q' is required",
                    status_code=400
                )
            )

        notes = search_notes_by_content(search_term)

        return json_response(
            ListAPIContext(
                entity_table_name=ENTITY_NAME,
                items=notes,
                total_count=len(notes)
            )
        )
    except Exception as e:
        logger.error(f"Error searching notes: {e}", exc_info=True)
        return json_response(
            ErrorAPIContext(
                message=f"Error searching notes: {str(e)}",
                status_code=500
            )
        )


logger.info(f"{ENTITY_PLURAL_NAME} API routes registered successfully.")