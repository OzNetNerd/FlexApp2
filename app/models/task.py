import logging
from app.models.base import db, BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)


class Task(BaseModel):
    """Represents a task associated with an entity like a company, contact, or opportunity.

    Tasks store details for tracking progress, due dates, and ownership.

    Attributes:
        title (str): Short summary of the task.
        description (str): Detailed explanation of the task.
        due_date (datetime): Deadline for task completion.
        status (str): Current task status (Pending, In Progress, Completed).
        priority (str): Priority level (Low, Medium, High).
        notable_type (str): The type of object this task is linked to.
        notable_id (int): The ID of the object this task is linked to.
    """

    __tablename__ = "tasks"

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="Pending")
    priority = db.Column(db.String(20), default="Medium")

    # Setting default values for notable_type and notable_id
    notable_type = db.Column(db.String(50), nullable=False, default="User")
    notable_id = db.Column(db.Integer, nullable=False, default=1)

    __field_order__ = {
        "Task Info": [
            {
                "name": "title",
                "label": "Title",
                "type": "text",
                "tab": "About",
                "section": "Task Info",
                "required": True,
            },
            {
                "name": "description",
                "label": "Description",
                "type": "textarea",
                "tab": "About",
                "section": "Task Info",
            },
            {
                "name": "due_date",
                "label": "Due Date",
                "type": "date",
                "tab": "About",
                "section": "Task Info",
            },
            {
                "name": "status",
                "label": "Status",
                "type": "select",
                "options": [
                    {"value": "Pending", "label": "Pending"},
                    {"value": "In Progress", "label": "In Progress"},
                    {"value": "Completed", "label": "Completed"},
                ],
                "tab": "About",
                "section": "Task Info",
                "required": True,
            },
            {
                "name": "priority",
                "label": "Priority",
                "type": "select",
                "options": [
                    {"value": "Low", "label": "Low"},
                    {"value": "Medium", "label": "Medium"},
                    {"value": "High", "label": "High"},
                ],
                "tab": "About",
                "section": "Task Info",
            },
        ],
        "Linked Entity": [
            {
                "name": "notable_type",
                "label": "Linked To (Type)",
                "type": "hidden",
                "default": "User",
                "tab": "Details",
                "section": "Linked Entity",
            },
            {
                "name": "notable_id",
                "label": "Linked To (ID)",
                "type": "hidden",
                "default": "1",
                "tab": "Details",
                "section": "Linked Entity",
            },
        ],
    }

    def __repr__(self) -> str:
        """Readable string representation.

        Returns:
            str: Summary with task title.
        """
        return f"<Task {self.title}>"

    def save(self, notable_type: str = "User", notable_id: int = 1) -> "Task":
        """Persist task to the database with logging.

        Args:
            notable_type (str): The type of object linked to the task. Defaults to "User".
            notable_id (int): The ID of the object linked to the task. Defaults to 1.

        Returns:
            Task: The saved task instance.
        """
        # Ensure notable_type and notable_id are set before saving
        if not self.notable_type:
            self.notable_type = notable_type
        if not self.notable_id:
            self.notable_id = notable_id

        if not self.notable_type or not self.notable_id:
            raise ValueError("Both 'notable_type' and 'notable_id' must be provided.")

        logger.debug(f"Saving task '{self.title}' with status {self.status}")
        super().save()
        logger.info(f"Task '{self.title}' saved successfully.")
        return self

    def delete(self) -> None:
        """Remove task from the database with logging."""
        logger.debug(f"Deleting task '{self.title}'")
        super().delete()
        logger.info(f"Task '{self.title}' deleted successfully.")

    @classmethod
    def create_from_form(cls, form_data):
        """Create a new task from form data.

        Args:
            form_data (dict): Form data containing task fields

        Returns:
            Task: The created task instance
        """
        # Ensure notable_type and notable_id are present
        if "notable_type" not in form_data or not form_data["notable_type"]:
            form_data["notable_type"] = "User"

        if "notable_id" not in form_data or not form_data["notable_id"]:
            # Try to get user ID from the session or set default
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

        # Handle date if provided
        if form_data.get("due_date"):
            try:
                if isinstance(form_data["due_date"], str):
                    task.due_date = datetime.strptime(form_data["due_date"], "%Y-%m-%d")
                else:
                    task.due_date = form_data["due_date"]
            except ValueError:
                logger.warning(f"Invalid date format for due_date: {form_data['due_date']}")

        task.save()
        return task
