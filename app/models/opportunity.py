from app.models.base import db, BaseModel
import logging

logger = logging.getLogger(__name__)

class Opportunity(db.Model, BaseModel):
    """Represents a sales opportunity linked to a company.

    Opportunities track deal stages, potential value, and related notes.

    Attributes:
        name (str): Title of the opportunity.
        description (str): Summary or notes about the opportunity.
        status (str): Current status (e.g., New, Won, Lost).
        stage (str): Sales pipeline stage (e.g., Prospecting).
        value (float): Estimated deal value.
        company_id (int): FK to the related company.
        notes (list[Note]): Notes linked via polymorphic relationship.
        __field_order__ (list[dict]): Field metadata for UI rendering.
    """

    __tablename__ = "opportunities"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="New")
    stage = db.Column(db.String(50), default="Prospecting")
    value = db.Column(db.Float, default=0.0)

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))

    notes = db.relationship(
        "Note",
        primaryjoin="and_(Note.notable_id == foreign(Opportunity.id), Note.notable_type == 'Opportunity')",
    )

    __field_order__ = [
        {"name": "name", "label": "Name", "type": "text", "required": True, "section": "About"},
        {"name": "description", "label": "Description", "type": "textarea", "section": "About"},
        {"name": "company.name", "label": "Company Name", "type": "text", "readonly": True, "section": "About"},
        {"name": "stage", "label": "Stage", "type": "text", "section": "Details"},
        {"name": "status", "label": "Status", "type": "text", "section": "Details"},
        {"name": "value", "label": "Value", "type": "number", "section": "Details"},
        {"name": "created_at", "label": "Created At", "type": "datetime", "readonly": True, "section": "Record Info"},
        {"name": "updated_at", "label": "Updated At", "type": "datetime", "readonly": True, "section": "Record Info"},
    ]

    def __repr__(self) -> str:
        """Readable string representation.

        Returns:
            str: Identifier showing the opportunity name.
        """
        return f"<Opportunity {self.name}>"

    def save(self):
        """Persist opportunity to the database with logging.

        Returns:
            Opportunity: The saved instance.
        """
        logger.debug(
            f"Saving opportunity with name {self.name} and status {self.status}"
        )
        super().save()
        logger.info(f"Opportunity '{self.name}' saved successfully.")
        return self

    def delete(self):
        """Remove opportunity from the database with logging.

        Returns:
            None
        """
        logger.debug(f"Deleting opportunity with name {self.name}")
        super().delete()
        logger.info(f"Opportunity '{self.name}' deleted successfully.")

    @property
    def crisp_summary(self) -> float | None:
        """Compute average CRISP score for all related contacts.

        Returns:
            float | None: Average CRISP score across all involved contacts.
        """
        contacts = {
            rel.contact for note in self.notes for rel in note.author.relationships
        }
        scores = [c.crisp_summary for c in contacts if c.crisp_summary is not None]

        if not scores:
            return None

        return round(sum(scores) / len(scores), 2)
