from app.models.base import BaseModel, db
from app.utils.app_logging import get_logger

logger = get_logger()


class Opportunity(BaseModel):
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)

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
        return f"<Opportunity {self.name!r}>"

    def save(self) -> "Opportunity":
        """Persist opportunity to the database with logging.

        Returns:
            Opportunity: The saved instance.
        """
        logger.info(f"Saving opportunity with name {self.name!r} and status {self.status!r}")
        super().save()
        logger.info(f"Opportunity {self.name!r} saved successfully.")
        return self

    def delete(self) -> None:
        """Remove opportunity from the database with logging."""
        logger.info(f"Deleting opportunity with name {self.name!r}")
        super().delete()
        logger.info(f"Opportunity {self.name!r} deleted successfully.")

    @property
    def crisp_summary(self) -> float | None:
        """Compute average CRISP score for all related contacts.

        Returns:
            float | None: Average CRISP score across all involved contacts.
        """
        try:
            contacts = set()

            if hasattr(self.notes, "__iter__") and not isinstance(self.notes, str):
                for note in self.notes:
                    if hasattr(note, "author") and hasattr(note.author, "relationships"):
                        for rel in note.author.relationships:
                            if hasattr(rel, "contact"):
                                contacts.add(rel.contact)
            elif hasattr(self.notes, "author") and hasattr(self.notes.author, "relationships"):
                for rel in self.notes.author.relationships:
                    if hasattr(rel, "contact"):
                        contacts.add(rel.contact)

            scores = [
                c.crisp_summary for c in contacts
                if hasattr(c, "crisp_summary") and c.crisp_summary is not None
            ]

            if not scores:
                return None

            return round(sum(scores) / len(scores), 2)
        except Exception as e:
            logger.error(f"Error calculating CRISP summary: {e!r}")
            return None
