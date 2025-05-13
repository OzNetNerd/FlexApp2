# app/routes/api/pages/contacts/__init__.py

from flask import Blueprint

ENTITY_NAME = "Contact"
ENTITY_PLURAL_NAME = "Contacts"

# Create the main blueprint
contacts_api_bp = Blueprint(f"{ENTITY_PLURAL_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

# Import all route modules to register their routes with the blueprint
from app.routes.api.pages.contacts import crud, dashboard, filters, statistics