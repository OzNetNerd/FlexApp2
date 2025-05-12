# app/services/task/analytics.py
from datetime import datetime, timedelta
import random
from app.models.pages.task import Task
from app.models.base import db
from app.services.service_base import ServiceBase


class TaskAnalyticsService(ServiceBase):
    """Service for task analytics and statistics."""

    def __init__(self):
        """Initialize the Task analytics service."""
        super().__init__()

    def get_dashboard_stats(self):
        """Get basic statistics for the dashboard."""
        total_tasks = Task.query.count()
        completed_count = db.session.query(Task).filter(Task.status == "completed").count()
        in_progress_count = db.session.query(Task).filter(Task.status == "in_progress").count()
        not_started_count = db.session.query(Task).filter(Task.status == "pending").count()
        overdue_tasks = db.session.query(Task).filter(
            Task.due_date < datetime.now().date(),
            Task.status != "completed"
        ).count()
        due_today = db.session.query(Task).filter(Task.due_date == datetime.now().date()).count()

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_count,
            "in_progress_tasks": in_progress_count,
            "pending_tasks": not_started_count,
            "overdue_tasks": overdue_tasks,
            "due_today": due_today,
        }

    def get_engagement_segments(self):
        """Get task status segments with percentages."""
        total_tasks = Task.query.count()
        completed_count = db.session.query(Task).filter(Task.status == "completed").count()
        in_progress_count = db.session.query(Task).filter(Task.status == "in_progress").count()
        not_started_count = db.session.query(Task).filter(Task.status == "pending").count()

        return {
            "completed": {
                "count": completed_count,
                "percentage": self._calculate_percentage(completed_count, total_tasks)
            },
            "in_progress": {
                "count": in_progress_count,
                "percentage": self._calculate_percentage(in_progress_count, total_tasks)
            },
            "not_started": {
                "count": not_started_count,
                "percentage": self._calculate_percentage(not_started_count, total_tasks)
            },
        }

    def prepare_completion_data(self):
        """Generate sample activity data for the chart."""
        days = []
        completed_tasks = []
        new_tasks = []

        today = datetime.now().date()

        for i in range(7):
            day = today - timedelta(days=i)
            day_name = day.strftime("%a %d")
            days.append(day_name)

            completed_tasks.append(random.randint(1, 10))
            new_tasks.append(random.randint(3, 15))

        days.reverse()
        completed_tasks.reverse()
        new_tasks.reverse()

        return {"labels": days, "completed_tasks": completed_tasks, "new_tasks": new_tasks}

    def get_statistics(self):
        """Get detailed statistics about tasks."""
        total_tasks = Task.query.count()
        completed_tasks = db.session.query(Task).filter(Task.status == "completed").count()
        in_progress_tasks = db.session.query(Task).filter(Task.status == "in_progress").count()
        pending_tasks = db.session.query(Task).filter(Task.status == "pending").count()
        high_priority = db.session.query(Task).filter(Task.priority == "high").count()
        medium_priority = db.session.query(Task).filter(Task.priority == "medium").count()
        low_priority = db.session.query(Task).filter(Task.priority == "low").count()
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
        """Calculate percentage value."""
        if total == 0:
            return 0
        return round((count / total) * 100)