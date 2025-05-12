from flask import request
from flask_login import login_required
from app.services.task import TaskService
from app.routes.web.pages.tasks import tasks_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

task_service = TaskService()

@tasks_bp.route("/", methods=["GET"], endpoint="index")
@login_required
def tasks_dashboard():
    # Get statistics and data from service
    stats = task_service.get_dashboard_stats()
    top_tasks = task_service.get_top_tasks()
    segments = task_service.get_engagement_segments()
    completion_data = task_service.prepare_completion_data()
    upcoming_tasks = task_service.get_upcoming_tasks()

    # Create context for the dashboard view
    context = WebContext(
        title="Tasks Dashboard",
        read_only=True,
        stats=stats,
        segments=segments,
        upcoming_tasks=upcoming_tasks,
        completion_data=completion_data
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/tasks/dashboard.html",
        context=context,
        error_message="An error occurred while rendering the tasks dashboard",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)