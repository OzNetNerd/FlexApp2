# app/routes/api/pages/users/__init__.py

from flask import Blueprint

ENTITY_NAME = "User"
ENTITY_PLURAL_NAME = "Users"

# Create the main blueprint
users_api_bp = Blueprint(f"{ENTITY_PLURAL_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

# Import all route modules to register their routes with the blueprint
from app.routes.api.pages.users import crud, dashboard, filters, statistics