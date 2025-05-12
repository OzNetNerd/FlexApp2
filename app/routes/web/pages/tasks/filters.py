from flask import request
from flask_login import login_required
from app.services.task import TaskService
from app.routes.web.pages.tasks import tasks_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

task_service = TaskService()

@tasks_bp.route("/filtered", methods=["GET"])
@login_required
def filtered_tasks():
    # Get filter parameters
    filters = {
        "status": request.args.get("status"),
        "priority": request.args.get("priority"),
        "due_date": request.args.get("due_date")
    }

    # Get filtered tasks from service
    tasks = task_service.get_filtered_tasks(filters)

    # Create context for the filtered view
    context = WebContext(
        title="Filtered Tasks",
        read_only=True,
        tasks=tasks,
        filters=filters
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/tasks/filtered.html",
        context=context,
        error_message="An error occurred while rendering the filtered tasks page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)