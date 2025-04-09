import logging
from flask import jsonify, request
from app.routes.blueprint_factory import create_blueprint
from app.models import Task
from app.services.crud_service import CRUDService

logger = logging.getLogger(__name__)

# Create API blueprint with /api prefix for tasks
tasks_api_bp = create_blueprint("api_tasks", url_prefix="/api/tasks")
task_service = CRUDService(Task)


@tasks_api_bp.route("/", methods=["GET"])
def get_all_tasks():
    """Get all tasks."""
    tasks = task_service.get_all()
    return jsonify([task.to_dict() for task in tasks])


@tasks_api_bp.route("/<int:entity_id>", methods=["GET"])
def get_task(entity_id):
    """Get a specific task."""
    task = task_service.get_by_id(entity_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())


@tasks_api_bp.route("/", methods=["POST"])
def create_task():
    """Create a new task."""
    data = request.get_json()
    # Validate required fields
    for field in ["title", "status"]:
        if field not in data:
            return jsonify({"error": f"{field} is required."}), 400
    result = task_service.create(data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201


@tasks_api_bp.route("/<int:entity_id>", methods=["PUT"])
def update_task(entity_id):
    """Update a task."""
    data = request.get_json()
    result = task_service.update(entity_id, data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@tasks_api_bp.route("/<int:entity_id>", methods=["DELETE"])
def delete_task(entity_id):
    """Delete a task."""
    result = task_service.delete(entity_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


logger.info("Task API routes instantiated successfully.")
