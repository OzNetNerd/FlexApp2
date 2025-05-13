# app/routes/api/pages/tasks/filters.py

from flask import jsonify, request
from app.services.task import TaskService
from app.routes.api.pages.tasks import tasks_api_bp

# Initialize specialized service
task_service = TaskService()


@tasks_api_bp.route("/filtered", methods=["GET"])
def get_filtered_tasks():
    """Get tasks based on filter criteria."""
    filters = {
        "status": request.args.get("status"),
        "priority": request.args.get("priority"),
        "due_date_from": request.args.get("due_date_from"),
        "due_date_to": request.args.get("due_date_to"),
        "assigned_to": request.args.get("assigned_to"),
    }
    tasks = task_service.get_filtered_tasks(filters)
    return jsonify([task.to_dict() for task in tasks])
