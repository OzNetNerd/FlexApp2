# app/routes/api/clients/pages/tasks.py

from app.routes.api.clients import ApiClient

class TaskApiClient(ApiClient):
    """Client for interacting with the Task API."""

    def __init__(self):
        super().__init__('/api/tasks')

    # CRUD operations
    def get_all(self):
        """Get all tasks."""
        return self.get(f"{self.base_path}")

    def get_by_id(self, task_id):
        """Get a task by ID."""
        return self.get(f"{self.base_path}/{task_id}")

    def create(self, data):
        """Create a new task."""
        return self.post(f"{self.base_path}", data)

    def update(self, task_id, data):
        """Update a task."""
        return self.put(f"{self.base_path}/{task_id}", data)

    def delete_task(self, task_id):
        """Delete a task."""
        return self.delete(f"{self.base_path}/{task_id}")

    # Dashboard operations
    def get_dashboard_stats(self):
        """Get statistics for the tasks dashboard."""
        return self.get(f"{self.base_path}/dashboard/stats")

    def get_top_tasks(self, limit=5):
        """Get top tasks by priority."""
        return self.get(f"{self.base_path}/dashboard/top", params={"limit": limit})

    def get_status_breakdown(self):
        """Get tasks breakdown by status."""
        return self.get(f"{self.base_path}/dashboard/status")

    def get_overdue_tasks(self):
        """Get overdue tasks."""
        return self.get(f"{self.base_path}/dashboard/overdue")

    # Statistics operations
    def get_statistics(self):
        """Get comprehensive statistics for the statistics page."""
        return self.get(f"{self.base_path}/statistics")

    # Filter operations
    def get_filtered_tasks(self, filters):
        """Get tasks based on filter criteria."""
        return self.get(f"{self.base_path}/filtered", params=filters)