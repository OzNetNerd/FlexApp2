# app/services/task/analytics.py

from datetime import datetime, timedelta
from sqlalchemy import func
from app.models.pages.task import Task
from app.models.base import db
from app.services.service_base import ServiceBase


class TaskAnalyticsService(ServiceBase):
    """Service for task analytics and statistics."""

    def __init__(self):
        """Initialize the Task analytics service."""
        super().__init__()

    def get_total_tasks(self):
        """Get the total number of tasks."""
        return Task.query.count()

    def get_dashboard_statistics(self):
        """Get statistics for the tasks dashboard."""
        total_tasks = self.get_total_tasks()

        return {
            "total_tasks": total_tasks,
            "completed_tasks": db.session.query(Task).filter(Task.status == "completed").count(),
            "in_progress_tasks": db.session.query(Task).filter(Task.status == "in_progress").count(),
            "pending_tasks": db.session.query(Task).filter(Task.status == "pending").count(),
            "overdue_tasks": db.session.query(Task).filter(Task.due_date < datetime.now().date(),
                                                           Task.status != "completed").count(),
            "due_today": db.session.query(Task).filter(Task.due_date == datetime.now().date()).count(),
        }

    def get_top_tasks(self, limit=5):
        """Get top tasks by priority."""
        return (
            db.session.query(Task)
            .filter(Task.status != "completed")
            .order_by(
                Task.priority.desc(),
                Task.due_date.asc()
            )
            .limit(limit)
            .all()
        )

    def get_engagement_segments(self):
        """Get task segments by status."""
        total_tasks = self.get_total_tasks()

        completed_count = db.session.query(Task).filter(Task.status == "completed").count()
        in_progress_count = db.session.query(Task).filter(Task.status == "in_progress").count()
        pending_count = db.session.query(Task).filter(Task.status == "pending").count()

        return [
            {
                "name": "Completed",
                "count": completed_count,
                "percentage": self._calculate_percentage(completed_count, total_tasks),
            },
            {
                "name": "In Progress",
                "count": in_progress_count,
                "percentage": self._calculate_percentage(in_progress_count, total_tasks),
            },
            {
                "name": "Pending",
                "count": pending_count,
                "percentage": self._calculate_percentage(pending_count, total_tasks),
            },
        ]

    def prepare_completion_data(self, days_back=7):
        """Prepare completion data for the chart."""
        days = []
        completed_tasks = []
        new_tasks = []

        today = datetime.now().date()

        for i in range(days_back):
            day = today - timedelta(days=i)
            day_name = day.strftime("%a %d")

            # Start and end of day
            start_date = datetime.combine(day, datetime.min.time())
            end_date = datetime.combine(day, datetime.max.time())

            # Completed tasks in this day
            completed_in_day = Task.query.filter(
                Task.updated_at >= start_date,
                Task.updated_at <= end_date,
                Task.status == "completed"
            ).count()

            # New tasks in this day
            new_in_day = Task.query.filter(
                Task.created_at >= start_date,
                Task.created_at <= end_date
            ).count()

            days.append(day_name)
            completed_tasks.append(completed_in_day)
            new_tasks.append(new_in_day)

        # Reverse lists to display chronologically
        days.reverse()
        completed_tasks.reverse()
        new_tasks.reverse()

        return {"labels": days, "completed_tasks": completed_tasks, "new_tasks": new_tasks}

    def get_statistics(self):
        """Get comprehensive statistics for the statistics page."""
        total_tasks = self.get_total_tasks()

        # Tasks by status
        completed_tasks = db.session.query(Task).filter(Task.status == "completed").count()
        in_progress_tasks = db.session.query(Task).filter(Task.status == "in_progress").count()
        pending_tasks = db.session.query(Task).filter(Task.status == "pending").count()

        # Tasks by priority
        high_priority = db.session.query(Task).filter(Task.priority == "high").count()
        medium_priority = db.session.query(Task).filter(Task.priority == "medium").count()
        low_priority = db.session.query(Task).filter(Task.priority == "low").count()

        # Overdue tasks
        overdue_tasks = db.session.query(Task).filter(
            Task.due_date < datetime.now().date(),
            Task.status != "completed"
        ).count()

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_tasks": pending_tasks,
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "overdue_tasks": overdue_tasks,
        }

    def _calculate_percentage(self, count, total):
        """Calculate percentage with safety check for division by zero."""
        if total == 0:
            return 0
        return round((count / total) * 100)