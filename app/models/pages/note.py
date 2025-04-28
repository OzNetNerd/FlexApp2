from app.models.base import BaseModel, db
from app.utils.app_logging import get_logger

logger = get_logger()


class Note(BaseModel):
    __tablename__ = "notes"

    # Add this primary key column
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)
    processed_content = db.Column(db.Text)

    notable_type = db.Column(db.String(50), nullable=False)
    notable_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

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
        logger.info(f"Saving note with id {self.id} for {self.notable_type} ID {self.notable_id}")
        super().save()
        logger.info(f"Note with id {self.id} saved successfully.")
        return self

    def delete(self) -> None:
        """Remove note from the database with logging."""
        logger.info(f"Deleting note with id {self.id}")
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
