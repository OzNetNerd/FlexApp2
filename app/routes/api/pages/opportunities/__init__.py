# app/routes/api/pages/opportunities/__init__.py

from flask import Blueprint

ENTITY_NAME = "Opportunity"
ENTITY_PLURAL_NAME = "Opportunities"

# Create the main blueprint
opportunities_api_bp = Blueprint(f"{ENTITY_PLURAL_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

# Import all route modules to register their routes with the blueprint
from app.routes.api.pages.opportunities import crud, dashboard, filters, statistics