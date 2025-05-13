# app/routes/api/pages/tasks.py

from flask import Blueprint

from app.models import Task
from app.routes.api.route_registration import ApiCrudRouteConfig
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()

ENTITY_NAME = "Task"
ENTITY_PLURAL_NAME = "Tasks"

tasks_api_bp = Blueprint(f"{ENTITY_PLURAL_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

task_service = CRUDService(Task)

task_api_crud_config = ApiCrudRouteConfig(blueprint=tasks_api_bp, entity_table_name=ENTITY_NAME, service=task_service)
