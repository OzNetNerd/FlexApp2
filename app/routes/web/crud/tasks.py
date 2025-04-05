import logging
from flask import Blueprint, abort, render_template
from flask_login import current_user
from datetime import datetime

from app.models.task import Task
from app.routes.web.crud.components.generic_crud_routes import GenericWebRoutes
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import Context

logger = logging.getLogger(__name__)

# Define the blueprint
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


class TasksCRUDRoutes(GenericWebRoutes):
    """
    Custom CRUD routes for Task model.
    """

    def _preprocess_form_data(self, form_data):
        return form_data

    def index(self):
        """Overrides the default index for Tasks."""
        if not current_user.is_authenticated:
            abort(403)

        return render_template(
            self.index_template,
            title="Tasks",
        )


# Register the CRUD route handler
tasks_routes = TasksCRUDRoutes(
    blueprint=tasks_bp,
    model=Task,
    index_template="pages/tables/tasks.html",
    required_fields=[],
    unique_fields=[],
)

# Custom route: Show overdue tasks
@tasks_bp.route("/overdue")
def overdue_tasks():
    """Show overdue tasks."""
    overdue = Task.query.filter(
        Task.due_date < datetime.utcnow(),
        Task.status != "completed",
        Task.assigned_to == current_user.id
    ).all()

    context = Context(title="Overdue Tasks", items=overdue)
    return render_safely("pages/tasks/overdue.html", context, "Failed to load overdue tasks.")


# Custom route: Extended task view
@tasks_bp.route("/<int:item_id>/extended")
def view_extended(item_id):
    """View task with additional context."""
    task = Task.query.get_or_404(item_id)
    context = Context(title=f"Task: {task.title}", item=task)
    return render_safely("pages/crud/view.html", context, "Failed to load task details.")


logger.info("Task routes setup successfully.")
