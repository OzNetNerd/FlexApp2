from flask import Blueprint

# Create the blueprint
home_bp = Blueprint("home_bp", __name__, url_prefix="/")
