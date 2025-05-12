# app/routes/api/pages/companies/__init__.py

from flask import Blueprint

ENTITY_NAME = "Company"
ENTITY_PLURAL_NAME = "Companies"

# Create the main blueprint
companies_api_bp = Blueprint(f"{ENTITY_PLURAL_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

# Import all route modules to register their routes with the blueprint
from app.routes.api.pages.companies import crud, dashboard, filters, statistics