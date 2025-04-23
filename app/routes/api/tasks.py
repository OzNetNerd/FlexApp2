# api/tasks.py
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig
from app.models import Task
from app.services.crud_service import CRUDService
from flask import Blueprint

from app.utils.app_logging import get_logger
logger = get_logger()

ENTITY_NAME = "Task"
ENTITY_PLURAL_NAME = "Tasks"

tasks_api_bp = Blueprint(f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")
task_service = CRUDService(Task)

# Register all standard CRUD API routes
task_api_crud_config = ApiCrudRouteConfig(blueprint=tasks_api_bp, entity_table_name=ENTITY_NAME, service=task_service)
register_api_crud_routes(task_api_crud_config)

logger.info(f"{ENTITY_PLURAL_NAME} API routes registered successfully.")
