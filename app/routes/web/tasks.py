from app.models import Task, Note
from app.routes.web import tasks_bp
from app.routes.web.generic import GenericWebRoutes
from app.routes.ui.tasks import get_task_tabs
import logging

logger = logging.getLogger(__name__)


# Create a custom CRUD routes class for Tasks
class TaskCRUDRoutes(GenericWebRoutes):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_view_context(self, item, context):
        """Add notes_model to the view context."""
        logger.debug(f"Adding 'notes_model' to the view context for Task {item.id}.")
        context["notes_model"] = Note


# Set up the CRUD routes for tasks
logger.debug("Setting up CRUD routes for Task model.")
task_routes = TaskCRUDRoutes(
    model=Task,
    blueprint=tasks_bp,
    index_template="tasks.html",
    required_fields=["title", "status"],
    unique_fields=[],
    get_tabs_function=get_task_tabs,
)

logger.info("Task CRUD routes setup successfully.")
