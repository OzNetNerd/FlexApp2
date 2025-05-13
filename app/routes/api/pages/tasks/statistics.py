# app/routes/api/pages/tasks/statistics.py

from flask import jsonify
from app.services.task import TaskService
from app.routes.api.pages.tasks import tasks_api_bp

# Initialize specialized service
task_service = TaskService()

@tasks_api_bp.route("/statistics", methods=["GET"])
def get_statistics():
    """Get comprehensive statistics for the statistics page."""
    stats = task_service.get_statistics()
    return jsonify(stats)