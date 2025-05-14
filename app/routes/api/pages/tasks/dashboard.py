# app/routes/api/pages/tasks/dashboard.py

from flask import jsonify, request
from app.services.task import TaskService
from app.routes.api.pages.tasks import tasks_api_bp

# Initialize specialized service
task_service = TaskService()


@tasks_api_bp.route("/dashboard/stats", methods=["GET"])
def get_dashboard_statistics():
    """Get statistics for the tasks dashboard."""
    stats = task_service.get_dashboard_statistics()
    return jsonify(stats)


@tasks_api_bp.route("/dashboard/top", methods=["GET"])
def get_top_tasks():
    """Get top tasks by priority."""
    limit = request.args.get("limit", 5, type=int)
    top_tasks = task_service.get_top_tasks(limit)
    return jsonify([task.to_dict() for task in top_tasks])


@tasks_api_bp.route("/dashboard/status", methods=["GET"])
def get_status_breakdown():
    """Get tasks breakdown by status."""
    status_data = task_service.get_status_breakdown()
    return jsonify(status_data)


@tasks_api_bp.route("/dashboard/overdue", methods=["GET"])
def get_overdue_tasks():
    """Get overdue tasks."""
    overdue_tasks = task_service.get_overdue_tasks()
    return jsonify([task.to_dict() for task in overdue_tasks])
