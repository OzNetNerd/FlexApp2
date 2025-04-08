# app/routes/home.py
import logging
from flask import Blueprint
from app.routes.base.web_utils import register_page_route

logger = logging.getLogger(__name__)

# Define the blueprint
home_bp = Blueprint("home_bp", __name__, url_prefix="/")

# Register the home page route
register_page_route(
    blueprint=home_bp,
    url="/",
    template_path="index.html",
    endpoint="home_index"
)
