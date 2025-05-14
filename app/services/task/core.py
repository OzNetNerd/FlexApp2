# app/services/task/core.py
from datetime import datetime, timedelta
from app.services.service_base import BaseFeatureService
from app.models.pages.task import Task


class TaskService(BaseFeatureService):
    def __init__(self):
        super().__init__(Task)

    def get_dashboard_statistics(self):
        """Get task dashboard statistics."""
        stats = super().get_dashboard_statistics()
        stats.update({
            "total_tasks": Task.query.count(),
            "completed_tasks": self.count_completed_tasks(),
            "in_progress_tasks": self.count_in_progress_tasks(),
            "pending_tasks": self.count_pending_tasks()
        })
        return stats

    def count_completed_tasks(self):
        """Count completed tasks."""
        return Task.query.filter(Task.status == "completed").count()

    def count_in_progress_tasks(self):
        """Count in-progress tasks."""
        return Task.query.filter(Task.status == "in_progress").count()

    def count_pending_tasks(self):
        """Count pending tasks."""
        return Task.query.filter(Task.status == "pending").count()

    def get_statistics(self):
        """Get task statistics."""
        return {
            "total_tasks": Task.query.count(),
            "completed_tasks": self.count_completed_tasks(),
            "in_progress_tasks": self.count_in_progress_tasks(),
            "pending_tasks": self.count_pending_tasks(),
            "overdue_tasks": self.count_overdue_tasks()
        }

    def count_overdue_tasks(self):
        """Count overdue tasks."""
        return Task.query.filter(Task.due_date < datetime.now().date(),
                                 Task.status != "completed").count()

    def get_filtered_tasks(self, filters):
        """Get filtered tasks based on criteria."""
        query = Task.query

        status = filters.get("status")
        if status:
            query = query.filter(Task.status == status)

        priority = filters.get("priority")
        if priority:
            query = query.filter(Task.priority == priority)

        due_date = filters.get("due_date")
        if due_date == "today":
            query = query.filter(Task.due_date == datetime.now().date())
        elif due_date == "this_week":
            today = datetime.now().date()
            end_of_week = today + timedelta(days=(6 - today.weekday()))
            query = query.filter(Task.due_date.between(today, end_of_week))
        elif due_date == "overdue":
            query = query.filter(Task.due_date < datetime.now().date(),
                                 Task.status != "completed")

        return query.order_by(Task.due_date.asc()).all()

    def get_top_tasks(self, limit=5):
        """Get top tasks (most recent)."""
        return Task.query.order_by(Task.created_at.desc()).limit(limit).all()

    def get_upcoming_tasks(self, limit=5):
        """Get upcoming tasks."""
        return (
            Task.query.filter(Task.due_date >= datetime.now().date())
            .order_by(Task.due_date.asc())
            .limit(limit)
            .all()
        )