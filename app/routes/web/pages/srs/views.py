from flask import request
from flask_login import login_required, current_user
from app.models.pages.srs import SRS
from app.routes.web.utils.context import TableContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.utils.app_logging import get_logger
from app.routes.web.pages.srs.blueprint import srs_bp
import json
from datetime import datetime

logger = get_logger()


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@srs_bp.route("/records", methods=["GET"])
@login_required
def records():
    """View all flashcards in a table format.

    Returns:
        HTML: Rendered table of all SRS cards
    """
    logger.info(f"User {current_user.id} accessing SRS records table")

    from app.services.srs import SRSService

    # Get data from service
    srs_service = SRSService()
    srs_cards = srs_service.get_filtered_cards(request.args.to_dict())

    # Convert to dict format for table
    table_data = [card.to_dict() for card in srs_cards]

    # Properly serialize to JSON with datetime handling
    json_data = json.dumps(table_data, default=json_serial)

    # Create appropriate context for the records view
    context = TableContext(
        model_class=SRS, read_only=True, action="view", show_heading=True, table_data=json_data  # Now sending pre-serialized JSON string
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/srs/records.html",
        context=context,
        error_message="An error occurred while rendering the SRS records page",
        endpoint_name=request.endpoint,
    )

    # Return the safely rendered template
    return render_safely(config)
