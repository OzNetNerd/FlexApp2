from flask import request
from flask_login import login_required, current_user
from app.models.pages.srs import SRS
from app.routes.web.utils.context import TableContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.utils.app_logging import get_logger
from app.routes.web.pages.srs.blueprint import srs_bp

logger = get_logger()


@srs_bp.route("/records", methods=["GET"])
@login_required
def records():
    """View all flashcards in a table format.

    Returns:
        HTML: Rendered table of all SRS cards
    """
    logger.info(f"User {current_user.id} accessing SRS records table")

    # Create appropriate context for the records view
    context = TableContext(
        model_class=SRS,
        read_only=True,
        action="view",
        show_heading=True
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/srs/records.html",
        context=context,
        error_message="An error occurred while rendering the SRS records page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)