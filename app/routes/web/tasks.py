# tasks.py

from flask import Blueprint
from app.routes.web.route_registration import register_crud_routes, CrudRouteConfig, CrudTemplates
from app.services.crud_service import CRUDService
from app.models.task import Task

from app.utils.app_logging import get_logger
logger = get_logger()

# Define the blueprint
tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

# Create a service instance
task_service = CRUDService(Task)

# Define custom templates for tasks
custom_templates = CrudTemplates(
    create="pages/crud/create_view_edit_task.html",
    view="pages/crud/create_view_edit_task.html",
    edit="pages/crud/create_view_edit_task.html",
)

# Log the custom templates for debugging purposes
logger.info(f"Custom templates: {custom_templates.to_dict()}")

# Register all standard CRUD routes with custom templates
task_crud_config = CrudRouteConfig(blueprint=tasks_bp, entity_table_name="Task", service=task_service, templates=custom_templates)
register_crud_routes(task_crud_config)
