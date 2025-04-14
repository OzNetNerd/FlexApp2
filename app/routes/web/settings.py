# app/routes/settings.py
import logging
from flask import Blueprint
from app.routes.web.route_registration import register_route, SimpleContext

logger = logging.getLogger(__name__)

# Define the blueprint
settings_bp = Blueprint("settings_bp", __name__, url_prefix="/settings")

# Register the settings page route
register_route(
    blueprint=settings_bp,
    url="/",
    template_path="pages/misc/settings.html",
    title="Settings",
    context_provider=SimpleContext,
    endpoint="index",  # This is needed for url_for('settings_bp.index') to work
)
