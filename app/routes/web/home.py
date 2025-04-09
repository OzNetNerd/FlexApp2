# app/routes/home.py
import logging
from flask import Blueprint
from app.routes.base.web_utils import register_route, SimpleContext

logger = logging.getLogger(__name__)

# Define the blueprint
home_bp = Blueprint("home_bp", __name__, url_prefix="/")


# Register the home page route
register_route(
    blueprint=home_bp,
    title="Welcome",
    url="/",
    template_path="home.html",
    endpoint="home",
    context_provider=SimpleContext,
)
