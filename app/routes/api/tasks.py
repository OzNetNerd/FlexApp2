# api/tasks.py

import logging
from app.routes.blueprint_factory import create_blueprint
from app.routes.api.route_registration import register_api_crud_routes, ApiCrudRouteConfig
from app.models import Task
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)

# Create API blueprint with /api prefix for tasks
tasks_api_bp = create_blueprint("api_tasks", url_prefix="/api/tasks")
task_service = CRUDService(Task)

# Register all standard CRUD API routes
task_api_crud_config = ApiCrudRouteConfig(
    blueprint=tasks_api_bp,
    entity_table_name="Task",
    service=task_service
)
register_api_crud_routes(task_api_crud_config)

# Custom routes can be added here if needed
# Example:
# @tasks_api_bp.route("/by-status/<status>", methods=["GET"])
# def get_tasks_by_status(status):
#     tasks = task_service.get_by_status(status)
#     return jsonify([task.to_dict() for task in tasks])

logger.info("Task API routes registered successfully.")