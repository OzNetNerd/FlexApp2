import logging
from app.models import Task
from app.routes.blueprint_factory import create_blueprint
from app.routes.base.crud_factory import register_crud_routes
from app.routes.base.components.template_renderer import render_safely
from app.routes.base.components.entity_handler import Context

logger = logging.getLogger(__name__)

# Create blueprint
tasks_bp = create_blueprint("tasks")

# Register standard CRUD routes
register_crud_routes(tasks_bp, "task")


# Add custom route handlers for tasks
@tasks_bp.route('/overdue')
def overdue_tasks():
    """Show overdue tasks."""
    from datetime import datetime
    from flask_login import current_user

    overdue = Task.query.filter(
        Task.due_date < datetime.utcnow(),
        Task.status != 'completed',
        Task.assigned_to == current_user.id
    ).all()

    context = Context(title="Overdue Tasks", items=overdue)
    return render_safely("pages/tasks/overdue.html", context, "Failed to load overdue tasks.")


# Custom task view with additional context
@tasks_bp.route('/<int:item_id>/extended')
def view_extended(item_id):
    """View task with additional context."""
    task = Task.query.get_or_404(item_id)

    context = Context(title=f"Task: {task.title}", item=task)

    # Add additional context that was in the original add_view_context method
    # This can include notes or other related information
    # context.notes_model = Note

    return render_safely("pages/crud/view.html", context, "Failed to load task details.")


logger.info("Task routes setup successfully.")