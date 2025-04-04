# app/routes/web/index.py
import logging
from flask import Blueprint
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import Context

logger = logging.getLogger(__name__)

index_bp = Blueprint("index", __name__)

@index_bp.route("/")
def index():
    logger.debug("Rendering dashboard/home page.")
    context = Context(title="Dashboard")
    fallback_message = "Sorry, we couldn't load the dashboard. Please try again later."
    return render_safely("index.html", context, fallback_message)
