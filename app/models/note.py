from models.base import db, BaseModel
import logging

logger = logging.getLogger(__name__)


class Note(db.Model, BaseModel):
    __tablename__ = 'notes'

    content = db.Column(db.Text, nullable=False)
    processed_content = db.Column(db.Text)

    notable_type = db.Column(db.String(50), nullable=False)  # e.g., 'Company', 'Contact', 'Opportunity'
    notable_id = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    __field_order__ = [
        ("Content", "content"),
        ("Processed", "processed_content"),
        ("Author", "author.username"),
        ("Created At", "created_at"),
        ("Updated At", "updated_at"),
    ]

    def __repr__(self):
        return f'<Note {self.id} on {self.notable_type} {self.notable_id}>'

    def save(self):
        logger.debug(f"Saving note with id {self.id} for {self.notable_type} ID {self.notable_id}")
        super().save()
        logger.info(f"Note with id {self.id} saved successfully.")

    def delete(self):
        logger.debug(f"Deleting note with id {self.id}")
        super().delete()
        logger.info(f"Note with id {self.id} deleted successfully.")

    @property
    def notable(self):
        """Return the related object based on notable_type and notable_id."""
        from models import Company, Contact, Opportunity  # Lazy import avoids circular
        mapping = {
            'Company': Company,
            'Contact': Contact,
            'Opportunity': Opportunity
        }
        model = mapping.get(self.notable_type)
        return model.query.get(self.notable_id) if model else None
