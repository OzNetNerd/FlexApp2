from flask import request
from flask_login import login_required
from app.services.task import TaskService
from app.routes.web.pages.tasks import tasks_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

task_service = TaskService()


@tasks_bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    # Get statistics from service
    stats = task_service.get_statistics()

    # Create context for the statistics view
    context = WebContext(
        title="Task Statistics",
        read_only=True,
        total_tasks=stats["total_tasks"],
        completed_tasks=stats["completed_tasks"],
        in_progress_tasks=stats["in_progress_tasks"],
        pending_tasks=stats["pending_tasks"],
        high_priority=stats["high_priority"],
        medium_priority=stats["medium_priority"],
        low_priority=stats["low_priority"],
        overdue_tasks=stats["overdue_tasks"],
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/tasks/statistics.html",
        context=context,
        error_message="An error occurred while rendering the task statistics page",
        endpoint_name=request.endpoint,
    )

    # Return the safely rendered template
    return render_safely(config)
