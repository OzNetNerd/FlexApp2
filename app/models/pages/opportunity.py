# app/models/opportunity.py

from datetime import datetime
from app.models.base import BaseModel, db
from app.utils.app_logging import get_logger

logger = get_logger()


class Opportunity(BaseModel):
    __tablename__ = "opportunities"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="active")
    stage = db.Column(db.String(50), default="qualification")
    value = db.Column(db.Float, default=0.0)
    priority = db.Column(db.String(20), default="medium")
    close_date = db.Column(db.DateTime)
    last_activity_date = db.Column(db.DateTime, default=datetime.now)

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))

    # Add this relationship for contact joins in queries
    contact_relationships = db.relationship(
        "Relationship",
        primaryjoin="and_(or_(and_(Relationship.entity1_type=='opportunity', foreign(Relationship.entity1_id)==Opportunity.id, Relationship.entity2_type=='contact'), and_(Relationship.entity2_type=='opportunity', foreign(Relationship.entity2_id)==Opportunity.id, Relationship.entity1_type=='contact')))",
        viewonly=True,
    )

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

    @property
    def contacts(self):
        """
        Retrieve Contacts linked to this Opportunity.
        Uses the Relationship model where this opportunity is linked to a contact.
        """
        from app.models.pages.contact import Contact

        contact_ids = []
        for rel in self.contact_relationships:
            if rel.entity1_type == "opportunity" and rel.entity2_type == "contact":
                contact_ids.append(rel.entity2_id)
            elif rel.entity2_type == "opportunity" and rel.entity1_type == "contact":
                contact_ids.append(rel.entity1_id)

        return Contact.query.filter(Contact.id.in_(contact_ids)).all() if contact_ids else []

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

            scores = [c.crisp_summary for c in contacts if hasattr(c, "crisp_summary") and c.crisp_summary is not None]

            if not scores:
                return None

            return round(sum(scores) / len(scores), 2)
        except Exception as e:
            logger.error(f"Error calculating CRISP summary: {e!r}")
            return None
