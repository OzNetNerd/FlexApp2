# app/routes/home.py

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.utils.app_logging import get_logger

logger = get_logger()
home_bp = Blueprint("home_bp", __name__, url_prefix="/")


@home_bp.route("/", methods=["GET"])
@login_required
def index():
    """Render the dashboard home page for authenticated users."""
    logger.info(f"Rendering dashboard for user {current_user.id}")
    return render_template("pages/home.html")
