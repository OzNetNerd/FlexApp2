# app/routes/api/pages/tasks/__init__.py

from flask import Blueprint

ENTITY_NAME = "Task"
ENTITY_PLURAL_NAME = "Tasks"

# Create the main blueprint
tasks_api_bp = Blueprint(f"{ENTITY_PLURAL_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

# Import all route modules to register their routes with the blueprint
from app.routes.api.pages.tasks import crud, dashboard, filters, statistics
