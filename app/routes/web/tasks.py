import logging
from flask import Blueprint
from app.routes.base.web_utils import register_crud_routes
from app.services.crud_service import CRUDService
from app.models.task import Task
from app.routes.base.web_utils import CrudRouteConfig

logger = logging.getLogger(__name__)

# Define the blueprint
tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

# Create a service instance
task_service = CRUDService(Task)

# Register all standard CRUD routes
task_crud_config = CrudRouteConfig(
    blueprint=tasks_bp,
    entity_name="Task",
    service=task_service
)
register_crud_routes(task_crud_config)