import logging
from app.models.base import db, BaseModel

logger = logging.getLogger(__name__)


class Note(BaseModel):
    """A comment or annotation linked to a CRM entity.

    Notes support polymorphic behavior by attaching to various models like
    Company, Contact, or Opportunity via `notable_type` and `notable_id`.

    Attributes:
        content (str): Raw text of the note.
        processed_content (str): Optional processed/HTML content.
        notable_type (str): The type of object this note is linked to.
        notable_id (int): The ID of the object this note is linked to.
        user_id (int): The user who created the note.
        __field_order__ (list[dict]): Field rendering metadata for UI.
    """

    __tablename__ = "notes"

    content = db.Column(db.Text, nullable=False)
    processed_content = db.Column(db.Text)

    notable_type = db.Column(db.String(50), nullable=False)  # e.g., 'Company', 'Contact', 'Opportunity'
    notable_id = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    __field_order__ = [
        {"name": "content", "label": "Content", "type": "textarea", "tab": "Post", "section": "Body"},
        {
            "name": "processed_content",
            "label": "Processed",
            "type": "textarea",
            "readonly": True,
            "tab": "Post",
            "section": "Body",
        },
        {
            "name": "author.username",
            "label": "Author",
            "type": "text",
            "readonly": True,
            "tab": "Post",
            "section": "Metadata",
        },
        {
            "name": "created_at",
            "label": "Created At",
            "type": "datetime",
            "readonly": True,
            "tab": "Post",
            "section": "Metadata",
        },
        {
            "name": "updated_at",
            "label": "Updated At",
            "type": "datetime",
            "readonly": True,
            "tab": "Post",
            "section": "Metadata",
        },
    ]

    def __repr__(self) -> str:
        """Readable string representation.

        Returns:
            str: Identifier and linked object type.
        """
        return f"<Note {self.id} on {self.notable_type} {self.notable_id}>"

    def save(self) -> "Note":
        """Persist note to the database with logging.

        Returns:
            Note: The saved note instance.
        """
        logger.debug(f"Saving note with id {self.id} for {self.notable_type} ID {self.notable_id}")
        super().save()
        logger.info(f"Note with id {self.id} saved successfully.")
        return self

    def delete(self) -> None:
        """Remove note from the database with logging."""
        logger.debug(f"Deleting note with id {self.id}")
        super().delete()
        logger.info(f"Note with id {self.id} deleted successfully.")

    @property
    def notable(self):
        """Resolve the actual related object (Company, Contact, Opportunity).

        Returns:
            Company | Contact | Opportunity | None: The linked object instance.
        """
        from app.models import Company, Contact, Opportunity  # Lazy import to avoid circular refs

        mapping = {"Company": Company, "Contact": Contact, "Opportunity": Opportunity}
        model = mapping.get(self.notable_type)
        return model.query.get(self.notable_id) if model else None
