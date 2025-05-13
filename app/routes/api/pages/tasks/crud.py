# app/routes/api/pages/tasks/crud.py

from flask import jsonify, request
from app.models import Task
from app.services.crud_service import CRUDService
from app.routes.api.pages.tasks import tasks_api_bp
from app.routes.api.route_registration import ApiCrudRouteConfig

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
