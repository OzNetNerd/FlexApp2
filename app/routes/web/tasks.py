from app.models import Task
from app.routes.web import tasks_bp
from app.routes.web.generic_crud_routes import GenericWebRoutes

import logging

logger = logging.getLogger(__name__)


# Create a custom CRUD routes class for Tasks
class TaskCRUDRoutes(GenericWebRoutes):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_view_context(self, item, context):
        """Add notes_model to the view context."""
        # logger.debug(f"Adding 'notes_model' to the view context for Task {item.id}.")
        # context["notes_model"] = Note
        pass


# Set up CRUD routes for managing tasks within the 'tasks_bp' blueprint.
# This configures routes for creating, reading, updating, and deleting tasks.
# The setup includes:
# - The `Task` model as the target for CRUD operations.
# - Required fields for task creation: `title` and `status`.
# - No uniqueness constraint is applied to any fields.
# - The template used for rendering the tasks table: `pages/tables/tasks.html`.
# - A custom function (`get_task_tabs`) to define the tabs displayed on the task creation page.
logger.debug("Setting up CRUD routes for Task model.")
task_routes = TaskCRUDRoutes(
    model=Task,
    blueprint=tasks_bp,
    index_template="pages/tables/tasks.html",
    required_fields=["title", "status"],
    unique_fields=[],
    # create_tabs_function=get_task_tabs,
)

logger.info("Task CRUD routes setup successfully.")
