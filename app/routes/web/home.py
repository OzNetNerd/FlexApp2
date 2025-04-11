# app/routes/home.py
import logging
from flask import Blueprint
from app.routes.web.components.web_utils import register_route, SimpleContext

logger = logging.getLogger(__name__)

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
