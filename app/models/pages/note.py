# app/models/note.py

from app.models.base import BaseModel, db
from app.models.mixins import NotableMixin
from app.utils.app_logging import get_logger

logger = get_logger()


class Note(BaseModel, NotableMixin):
    __tablename__ = "notes"

    content = db.Column(db.Text, nullable=False)
    processed_content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self) -> str:
        """Readable string representation.

        Returns:
            str: Identifier and linked object type.
        """
        return f"<Note {self.id} on {self.notable_type} {self.notable_id}>"
