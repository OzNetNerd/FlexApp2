# app/routes/web/tasks.py

from flask import Blueprint
from app.utils.app_logging import get_logger
from app.services.crud_service import CRUDService
from app.models import Task
from app.routes.web.route_registration import CrudRouteConfig, default_crud_templates

logger = get_logger()

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
task_service = CRUDService(Task)
templates = default_crud_templates("Task")

task_crud_config = CrudRouteConfig(
    blueprint=tasks_bp,
    entity_table_name="Task",
    service=task_service,
    templates=templates,
)
