# app/services/task/__init__.py
from app.services.service_base import ServiceBase, ServiceRegistry
from app.services.task.core import TaskCoreService
from app.services.task.analytics import TaskAnalyticsService


class TaskService(ServiceBase):
    """Main service for managing tasks."""

    def __init__(self):
        """Initialize the Task service with sub-services."""
        super().__init__()
        self.core = ServiceRegistry.get(TaskCoreService)
        self.analytics = ServiceRegistry.get(TaskAnalyticsService)

    # Core methods
    def get_by_id(self, task_id):
        """Get a task by ID."""
        return self.core.get_by_id(task_id)

    def get_all(self):
        """Get all tasks."""
        return self.core.get_all()

    def get_filtered_tasks(self, filters):
        """Get filtered tasks based on criteria."""
        return self.core.get_filtered_tasks(filters)

    def get_top_tasks(self, limit=5):
        """Get top tasks (most recent)."""
        return self.core.get_top_tasks(limit)

    def get_upcoming_tasks(self, limit=5):
        """Get upcoming tasks."""
        return self.core.get_upcoming_tasks(limit)

    # Analytics methods
    def get_dashboard_statistics(self):
        """Get basic statistics for the dashboard."""
        return self.analytics.get_dashboard_statistics()

    def get_engagement_segments(self):
        """Get task status segments with percentages."""
        return self.analytics.get_engagement_segments()

    def prepare_completion_data(self):
        """Generate sample activity data for the chart."""
        return self.analytics.prepare_completion_data()

    def get_statistics(self):
        """Get detailed statistics about tasks."""
        return self.analytics.get_statistics()
