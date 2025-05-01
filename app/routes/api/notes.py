from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint, request

from app.models import Note
from app.routes.api.route_registration import ApiCrudRouteConfig
from app.services.note_service import NoteService
from app.utils.app_logging import get_logger

logger = get_logger()

ENTITY_NAME = "Note"
ENTITY_PLURAL_NAME = "Notes"

notes_api_bp = Blueprint(f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

note_service = NoteService()

note_api_crud_config = ApiCrudRouteConfig(blueprint=notes_api_bp, entity_table_name=ENTITY_NAME, service=note_service)


@notes_api_bp.route("/query", methods=["GET"])
def query_notes():
    """Fetch notes with optional filters: notable_type, notable_id, date range, days ago, user_id, or search term."""
    query = Note.query
    filters = []
    nt = request.args.get("notable_type")
    nid = request.args.get("notable_id", type=int)
    if nt:
        filters.append(Note.notable_type == nt)
    if nid:
        filters.append(Note.notable_id == nid)

    # Handle from/to date parameters (ISO format)
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    if from_date and to_date:
        try:
            # Parse ISO format strings with timezone consideration
            start = datetime.fromisoformat(from_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(to_date.replace("Z", "+00:00"))
            logger.info(f"Date filter applied: from={start}, to={end}")
            filters.append(Note.created_at.between(start, end))
        except Exception as e:
            logger.error(f"Error parsing date range: {e}")

    # Legacy date range support
    start = request.args.get("start_date")
    end = request.args.get("end_date")
    if start and end and not (from_date and to_date):  # Only use if new format not provided
        try:
            s = datetime.strptime(start, "%Y-%m-%d")
            e = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)
            filters.append(Note.created_at.between(s, e))
        except Exception as e:
            logger.error(f"Error parsing legacy date range: {e}")

    days = request.args.get("days", type=int)
    if days is not None:
        cutoff = datetime.now(ZoneInfo("UTC")) - timedelta(days=days)
        filters.append(Note.created_at >= cutoff)

    uid = request.args.get("user_id", type=int)
    if uid:
        filters.append(Note.user_id == uid)

    q = request.args.get("q", "").strip()
    if q:
        pattern = f"%{q}%"
        filters.append(Note.content.ilike(pattern))

    if filters:
        query = query.filter(*filters)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 15, type=int)

    paginated = query.order_by(Note.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return {"data": [n.to_dict() for n in paginated.items], "total": paginated.total}


# You can add other manual routes (e.g. /filter/notable, /search) below as needed...

# Make sure to export the blueprint so it can be imported by the router
# This is critical for the application to register the routes
