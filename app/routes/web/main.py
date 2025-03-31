import logging
from app.routes.web import main_bp
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.form_handler import BasicContext

logger = logging.getLogger(__name__)


@main_bp.route("/")
def index():
    logger.debug("Serving main index page")
    context = BasicContext(title="Index")
    fallback_message = "Sorry, we couldn't load the homepage. Please try again later."
    return render_safely("index.html", context, fallback_message)
