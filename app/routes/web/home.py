# app/routes/home.py
from flask import Blueprint
from app.routes.web.route_registration import register_route, SimpleContext

from app.utils.app_logging import get_logger
logger = get_logger()

# Define the blueprint
home_bp = Blueprint("home_bp", __name__, url_prefix="/")


# Register the home page route
register_route(
    blueprint=home_bp,
    url="/",
    template_path="pages/misc/home.html",
    title="home",
    context_provider=SimpleContext,
)
