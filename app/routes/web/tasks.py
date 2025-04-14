import logging
from flask import Blueprint
from app.routes.web.route_registration import register_crud_routes, CrudRouteConfig, CrudTemplates
from app.services.crud_service import CRUDService
from app.models.task import Task

logger = logging.getLogger(__name__)

# Define the blueprint
tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

# Create a service instance
task_service = CRUDService(Task)

# Define custom templates for tasks
custom_templates = CrudTemplates(
    view="pages/crud/view_edit_tasks.html",
    edit="pages/crud/view_edit_tasks.html",
)

# Log the custom templates for debugging purposes
logger.info(f"Custom templates: {custom_templates.to_dict()}")

# Register all standard CRUD routes with custom templates
task_crud_config = CrudRouteConfig(
    blueprint=tasks_bp,
    entity_table_name="Task",
    service=task_service,
    templates=custom_templates
)
register_crud_routes(task_crud_config)
