import logging
from flask import Blueprint
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import SimpleContext

logger = logging.getLogger(__name__)

TABLE_NAME = 'Task'

# Define the blueprint manually for consistency with other modules
tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("/")
def index():
    """Tasks list page."""
    context = SimpleContext(title="Tasks", table_name=TABLE_NAME)
    return render_safely("pages/tables/tasks.html", context, "Failed to load tasks.")


@tasks_bp.route("/create")
def create():
    """Create task form."""
    context = SimpleContext(action="Create", table_name=TABLE_NAME)
    return render_safely("pages/crud/create.html", context, "Failed to load create task form.")


@tasks_bp.route("/<int:item_id>")
def view(item_id):
    """View task details."""
    context = SimpleContext(action="View", table_name=TABLE_NAME)
    return render_safely("pages/crud/view.html", context, "Failed to load task details.")


@tasks_bp.route("/<int:item_id>/edit")
def edit(item_id):
    """Edit task form."""
    context = SimpleContext(action="Edit", table_name=TABLE_NAME)
    return render_safely("pages/crud/edit.html", context, "Failed to load edit task form.")


@tasks_bp.route("/overdue")
def overdue_tasks():
    """Show overdue tasks."""
    context = SimpleContext(title="Overdue Tasks", table_name=TABLE_NAME)
    return render_safely("pages/tasks/overdue.html", context, "Failed to load overdue tasks.")


logger.info("Successfully set up 'Task' routes.")