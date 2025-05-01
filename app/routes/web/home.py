# app/routes/home.py

from flask import Blueprint
from flask_login import current_user, login_required

from app.routes.web.components.template_renderer import render_safely, RenderSafelyConfig
from app.utils.app_logging import get_logger

logger = get_logger()
home_bp = Blueprint("home_bp", __name__, url_prefix="/")


@home_bp.route("/", methods=["GET"])
@login_required
def index():
    """Render the dashboard home page for authenticated users."""
    logger.info(f"Rendering dashboard for user {current_user.id}")

    # Create configuration for render_safely
    config = RenderSafelyConfig(
        template_path="pages/misc/home.html",
        error_message="Error rendering dashboard home page",
        endpoint_name="index"
    )

    return render_safely(config)