import logging
from sqlalchemy.orm import foreign
from app.models.base import db, BaseModel
from app.models import contact_user_association

logger = logging.getLogger(__name__)


class Contact(BaseModel):
    """Represents a contact within a company in the CRM.

    Stores individual user details and links to relationships,
    companies, notes, and associated CRM users.

    Attributes:
        first_name (str): Contact's first name.
        last_name (str): Contact's last name.
        email (str): Email address.
        phone (str): Contact number.
        company (Company): Associated company.
        relationships (list[Relationship]): Associated relationships.
        notes (list[Note]): Polymorphic note objects.
        users (list[User]): CRM users linked to this contact.
        __field_order__ (list[dict]): Field metadata for UI rendering.
    """

    __tablename__ = "contacts"

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    company = db.relationship("Company", back_populates="contacts")

    relationships = db.relationship(
        "Relationship", back_populates="contact", cascade="all, delete-orphan"
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

    __field_order__ = [
        {"name": "first_name", "label": "First Name", "type": "text", "required": True,
         "tab": "About", "section": "Identity"},
        {"name": "last_name", "label": "Last Name", "type": "text", "required": True,
         "tab": "About", "section": "Identity"},
        {"name": "email", "label": "Email", "type": "email", "tab": "About", "section": "Contact Info"},
        {"name": "phone", "label": "Phone", "type": "text", "tab": "About", "section": "Contact Info"},
        {"name": "company_name", "label": "Company", "type": "text", "tab": "About", "section": "Company Info"},
        {"name": "created_at", "label": "Created At", "type": "text", "tab": "About",
         "section": "Record Info", "readonly": True},
        {"name": "updated_at", "label": "Updated At", "type": "text", "tab": "About",
         "section": "Record Info", "readonly": True},
        {"name": "crisp", "label": "CRISP", "type": "custom", "tab": "Insights", "section": "CRISP Score"},
    ]

    def __repr__(self) -> str:
        """String representation for debugging purposes.

        Returns:
            str: Full name of the contact.
        """
        return f"<Contact {self.first_name} {self.last_name}>"

    @property
    def full_name(self) -> str:
        """Concatenate first and last name.

        Returns:
            str: Full name.
        """
        logger.debug(f"Accessing full name for {self.first_name} {self.last_name}")
        return f"{self.first_name} {self.last_name}"

    @property
    def crisp_summary(self) -> float | None:
        """Calculate average CRISP score from all relationships.

        Returns:
            float | None: Average score or None if unavailable.
        """
        all_scores = [
            score.total_score
            for relationship in self.relationships
            for score in relationship.crisp_scores
            if score.total_score is not None
        ]
        return round(sum(all_scores) / len(all_scores), 2) if all_scores else None

    def get_relationship_with(self, user) -> "Relationship | None":
        """Return the relationship between this contact and a specific user.

        Args:
            user (User): The user to search for.

        Returns:
            Relationship | None: The relationship if found, otherwise None.
        """
        return next((rel for rel in self.relationships if rel.user_id == user.id), None)
