from flask import Blueprint
import logging
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import BasicContext

logger = logging.getLogger(__name__)
web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    """Render the dashboard/home page."""
    logger.debug("Rendering dashboard/home page.")
    context = BasicContext(title="Dashboard")
    fallback_message = "Sorry, we couldn't load the dashboard. Please try again later."
    return render_safely("index.html", context, fallback_message)
