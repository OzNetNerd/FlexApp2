# app/routes/api/pages/srs/__init__.py

from flask import Blueprint

ENTITY_NAME = "SRS"
ENTITY_PLURAL_NAME = ENTITY_NAME

# Create the main blueprint
srs_api_bp = Blueprint(f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

# Import all route modules to register their routes with the blueprint
from app.routes.api.pages.srs import crud, review, categories, stats