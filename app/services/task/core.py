# app/services/task/core.py
from datetime import datetime, timedelta
from app.models.pages.task import Task
from app.services.service_base import CRUDService
from app.services.validator_mixin import ValidatorMixin


class TaskCoreService(CRUDService, ValidatorMixin):
    """Core service for Task CRUD operations."""

    def __init__(self):
        """Initialize the Task core service."""
        super().__init__(model_class=Task)

    def get_filtered_tasks(self, filters):
        """Get filtered tasks based on criteria."""
        query = self.model_class.query

        status = filters.get("status")
        if status:
            query = query.filter(self.model_class.status == status)

        priority = filters.get("priority")
        if priority:
            query = query.filter(self.model_class.priority == priority)

        due_date = filters.get("due_date")
        if due_date == "today":
            query = query.filter(self.model_class.due_date == datetime.now().date())
        elif due_date == "this_week":
            today = datetime.now().date()
            end_of_week = today + timedelta(days=(6 - today.weekday()))
            query = query.filter(self.model_class.due_date.between(today, end_of_week))
        elif due_date == "overdue":
            query = query.filter(self.model_class.due_date < datetime.now().date(), self.model_class.status != "completed")

        return query.order_by(self.model_class.due_date.asc()).all()

    def get_top_tasks(self, limit=5):
        """Get top tasks (most recent)."""
        return self.model_class.query.order_by(self.model_class.created_at.desc()).limit(limit).all()

    def get_upcoming_tasks(self, limit=5):
        """Get upcoming tasks."""
        return (
            self.model_class.query.filter(self.model_class.due_date >= datetime.now().date())
            .order_by(self.model_class.due_date.asc())
            .limit(limit)
            .all()
        )
