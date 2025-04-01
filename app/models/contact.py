import logging
from app.models.base import db, BaseModel
from app.models import contact_user_association
from app.routes.base.components.form_handler import Tab, TabSection, TabEntry

logger = logging.getLogger(__name__)

class Contact(BaseModel):
    """Represents a contact within a company in the CRM."""

    __tablename__ = "contacts"

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    company = db.relationship("Company", back_populates="contacts")

    # Explicit foreign key and primaryjoin for relationships
    relationships = db.relationship(
        "Relationship",
        foreign_keys="[Relationship.entity1_id]",
        primaryjoin="and_(Contact.id == Relationship.entity1_id, Relationship.entity1_type == 'contact')",
        back_populates="contact",
        cascade="all, delete-orphan",
        overlaps="user,relationships"
    )

    notes = db.relationship(
        "Note",
        primaryjoin="and_(Note.notable_id == foreign(Contact.id), Note.notable_type == 'Contact')",
    )

    users = db.relationship(
        "User",
        secondary=contact_user_association,
        backref="assigned_contacts",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Contact {self.first_name} {self.last_name}>"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def crisp_summary(self) -> float | None:
        all_scores = [
            score.total_score for relationship in self.relationships for score in relationship.crisp_scores if score.total_score is not None
        ]
        return round(sum(all_scores) / len(all_scores), 2) if all_scores else None

    def get_relationship_with(self, user) -> "Relationship | None":
        return next((rel for rel in self.relationships if rel.user_id == user.id), None)