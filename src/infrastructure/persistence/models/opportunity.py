"""ORM models for the opportunity domain."""

from datetime import datetime
from infrastructure.persistence.models.base import BaseModel
from infrastructure.flask.extensions import db


class Opportunity(BaseModel):
    """
    ORM model for opportunities.

    Maps the Opportunity domain entity to the database.
    """

    __tablename__ = "opportunities"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="active")
    stage = db.Column(db.String(50), default="qualification")
    value = db.Column(db.Float, default=0.0)
    priority = db.Column(db.String(20), default="medium")
    close_date = db.Column(db.DateTime)
    last_activity_date = db.Column(db.DateTime, default=datetime.now)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_by = db.relationship("User", foreign_keys=[created_by_id])

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))

    contact_relationships = db.relationship(
        "Relationship",
        primaryjoin="and_(or_(and_(Relationship.entity1_type=='opportunity', "
                    "foreign(Relationship.entity1_id)==Opportunity.id, "
                    "Relationship.entity2_type=='contact'), "
                    "and_(Relationship.entity2_type=='opportunity', "
                    "foreign(Relationship.entity2_id)==Opportunity.id, "
                    "Relationship.entity1_type=='contact')))",
        viewonly=True,
    )

    notes = db.relationship(
        "Note",
        primaryjoin="and_(Note.notable_id == foreign(Opportunity.id), "
                    "Note.notable_type == 'Opportunity')",
    )

    def __repr__(self) -> str:
        """Return string representation of the opportunity."""
        return f"<Opportunity {self.name!r}>"