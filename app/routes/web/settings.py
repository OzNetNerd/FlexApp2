# app/routes/settings.py

from flask import Blueprint, render_template
from flask_login import login_required
from app.utils.app_logging import get_logger

logger = get_logger()
settings_bp = Blueprint("settings_bp", __name__, url_prefix="/settings")

@settings_bp.route("/", methods=["GET"])
@login_required
def index():
    """Render the application settings page for authenticated users."""
    logger.info("Rendering settings page")
    return render_template("pages/settings/index.html")
