# app/routes/api/pages/tasks/crud.py

from flask import jsonify, request
from app.models import Task
from app.services.crud_service import CRUDService
from app.routes.api.pages.tasks import tasks_api_bp
from app.routes.api.route_registration import ApiCrudRouteConfig
from app.utils.app_logging import get_logger

logger = get_logger()

# Register CRUD service and config
task_service = CRUDService(Task)
task_api_crud_config = ApiCrudRouteConfig(blueprint=tasks_api_bp, entity_table_name="Task", service=task_service)


# You can add additional CRUD-related endpoints here if needed
@tasks_api_bp.route("/", methods=["GET"])
def get_all():
    """Get all tasks."""
    tasks = task_service.get_all()
    return jsonify([task.to_dict() for task in tasks])


@tasks_api_bp.route("/<int:task_id>", methods=["GET"])
def get(task_id):
    """Get a task by ID."""
    task = task_service.get_by_id(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())

# For tasks
@tasks_api_bp.route("/<int:task_id>", methods=["PATCH"])
def update_task_field(task_id):
    """Update a single field of a task."""
    try:
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No update data provided"}), 400

        logger.info(f"Updating task {task_id} with data: {data}")

        # Get current task to validate it exists
        task = task_service.get_by_id(task_id)
        if not task:
            return jsonify({"error": f"Task with ID {task_id} not found"}), 404

        # Update only provided fields
        updated_task = task_service.update(task, data)
        return jsonify(updated_task.to_dict())
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        return jsonify({"error": f"Failed to update: {str(e)}"}), 500