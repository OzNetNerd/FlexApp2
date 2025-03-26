from app.models.base import db, BaseModel
import logging

logger = logging.getLogger(__name__)

class Task(db.Model, BaseModel):
    """Represents a task associated with a company, contact, opportunity, etc."""

    __tablename__ = "tasks"

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="Pending")
    priority = db.Column(db.String(20), default="Medium")

    notable_type = db.Column(db.String(50), nullable=False)
    notable_id = db.Column(db.Integer, nullable=False)

    __field_order__ = [
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
        {
            "name": "notable_type",
            "label": "Linked To (Type)",
            "type": "text",
            "readonly": True,
            "tab": "Details",
            "section": "Linked Entity",
        },
        {
            "name": "notable_id",
            "label": "Linked To (ID)",
            "type": "text",
            "readonly": True,
            "tab": "Details",
            "section": "Linked Entity",
        },
    ]

    def __repr__(self) -> str:
        return f"<Task {self.title}>"

    def save(self):
        logger.debug(f"Saving task '{self.title}' with status {self.status}")
        super().save()
        logger.info(f"Task '{self.title}' saved successfully.")
        return self

    def delete(self):
        logger.debug(f"Deleting task '{self.title}'")
        super().delete()
        logger.info(f"Task '{self.title}' deleted successfully.")
