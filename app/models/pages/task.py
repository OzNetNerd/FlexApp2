from datetime import datetime

from app.models.base import BaseModel, db
from app.utils.app_logging import get_logger

logger = get_logger()


class Task(BaseModel):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="Pending")
    priority = db.Column(db.String(20), default="Medium")
    notable_type = db.Column(db.String(50), nullable=False, default="User")
    notable_id = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationship with User model
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id],
                                  backref=db.backref('assigned_tasks', lazy='dynamic'))

    # Additional timestamp for completion tracking
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        """Readable string representation.

        Returns:
            str: Summary with task title.
        """
        return f"<Task {self.title!r}>"

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue.

        Returns:
            bool: True if due date is in the past and task is not completed.
        """
        return (
                self.due_date is not None and
                self.due_date < datetime.utcnow() and
                self.status.lower() != 'completed'
        )

    def save(self, notable_type: str = "User", notable_id: int = 1) -> "Task":
        """Persist task to the database with logging.

        Args:
            notable_type (str): The type of object linked to the task. Defaults to "User".
            notable_id (int): The ID of the object linked to the task. Defaults to 1.

        Returns:
            Task: The saved task instance.
        """
        if not self.notable_type:
            self.notable_type = notable_type
        if not self.notable_id:
            self.notable_id = notable_id

        # If status was changed to completed, set completed_at
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = datetime.utcnow()
        # If status was changed from completed, clear completed_at
        elif self.status != 'completed' and self.completed_at:
            self.completed_at = None

        logger.info(f"Saving task {self.title!r} with status {self.status!r}")
        super().save()
        logger.info(f"Task {self.title!r} saved successfully.")
        return self

    def delete(self) -> None:
        """Remove task from the database with logging."""
        logger.info(f"Deleting task {self.title!r}")
        super().delete()
        logger.info(f"Task {self.title!r} deleted successfully.")

    @classmethod
    def create_from_form(cls, form_data):
        """Create a new task from form data.

        Args:
            form_data (dict): Form data containing task fields

        Returns:
            Task: The created task instance
        """
        if "notable_type" not in form_data or not form_data["notable_type"]:
            form_data["notable_type"] = "User"

        if "notable_id" not in form_data or not form_data["notable_id"]:
            try:
                from flask_login import current_user

                if current_user and current_user.is_authenticated:
                    form_data["notable_id"] = current_user.id
                else:
                    form_data["notable_id"] = 1
            except ImportError:
                form_data["notable_id"] = 1

        task = cls(
            title=form_data["title"],
            description=form_data.get("description", ""),
            status=form_data.get("status", "Pending"),
            priority=form_data.get("priority", "Medium"),
            notable_type=form_data["notable_type"],
            notable_id=int(form_data["notable_id"]),
        )

        if form_data.get("due_date"):
            try:
                if isinstance(form_data["due_date"], str):
                    task.due_date = datetime.strptime(form_data["due_date"], "%Y-%m-%d")
                else:
                    task.due_date = form_data["due_date"]
            except ValueError:
                logger.warning(f"Invalid date format for due_date: {form_data['due_date']!r}")

        task.save()
        return task