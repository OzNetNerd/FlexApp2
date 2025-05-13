# app/routes/web/pages/home/home.py

from flask_login import current_user, login_required

from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.utils.app_logging import get_logger
from app.routes.web.utils.context import WebContext
from . import home_bp  # Import from the package

logger = get_logger()


@home_bp.route("/", methods=["GET"])
@login_required
def index():
    """Render the dashboard home page for authenticated users."""
    logger.info(f"Rendering dashboard for user {current_user.id}")

    # Create configuration for render_safely
    config = RenderSafelyConfig(
        template_path="pages/misc/home.html",
        error_message="Error rendering dashboard home page",
        endpoint_name="index",
        context=WebContext(title="Home Page"),
    )

    return render_safely(config)
