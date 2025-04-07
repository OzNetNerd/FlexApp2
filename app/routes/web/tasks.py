import logging
from flask import Blueprint
from app.routes.base.web_utils import register_routes
from app.services.crud_service import CRUDService
from app.models.task import Task

logger = logging.getLogger(__name__)

# Define the blueprint
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# Create a service instance
task_service = CRUDService(Task)

# Register all standard CRUD routes
register_routes(tasks_bp, "Task", service=task_service)
