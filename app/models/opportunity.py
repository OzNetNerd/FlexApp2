from app.models.base import db, BaseModel

from app.utils.app_logging import get_logger

logger = get_logger()


class Opportunity(BaseModel):
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

    def __repr__(self) -> str:
        """Readable string representation.

        Returns:
            str: Identifier showing the opportunity name.
        """
        return f"<Opportunity {self.name}>"

    def save(self) -> "Opportunity":
        """Persist opportunity to the database with logging.

        Returns:
            Opportunity: The saved instance.
        """
        logger.info(f"Saving opportunity with name {self.name} and status {self.status}")
        super().save()
        logger.info(f"Opportunity '{self.name}' saved successfully.")
        return self

    def delete(self) -> None:
        """Remove opportunity from the database with logging."""
        logger.info(f"Deleting opportunity with name {self.name}")
        super().delete()
        logger.info(f"Opportunity '{self.name}' deleted successfully.")

    @property
    def crisp_summary(self) -> float | None:
        """Compute average CRISP score for all related contacts.

        Returns:
            float | None: Average CRISP score across all involved contacts.
        """
        try:
            contacts = set()

            # Handle both cases: notes as a collection or as a single Note object
            if hasattr(self.notes, "__iter__") and not isinstance(self.notes, str):
                # It's iterable (like a list)
                for note in self.notes:
                    if hasattr(note, "author") and hasattr(note.author, "relationships"):
                        for rel in note.author.relationships:
                            if hasattr(rel, "contact"):
                                contacts.add(rel.contact)
            elif hasattr(self.notes, "author") and hasattr(self.notes.author, "relationships"):
                # It's a single Note object
                for rel in self.notes.author.relationships:
                    if hasattr(rel, "contact"):
                        contacts.add(rel.contact)

            scores = [c.crisp_summary for c in contacts if hasattr(c, "crisp_summary") and c.crisp_summary is not None]

            if not scores:
                return None

            return round(sum(scores) / len(scores), 2)
        except Exception as e:
            logger.error(f"Error calculating CRISP summary: {e}")
            return None
