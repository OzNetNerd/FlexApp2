from app.models.base import db, BaseModel
import logging

logger = logging.getLogger(__name__)

class Relationship(db.Model, BaseModel):
    """Represents a trust relationship between a user and a contact.

    This model allows the CRM to track interactions and trust metrics
    (via CRISP scores) between users and individual contacts.

    Attributes:
        user_id (int): FK to the CRM user.
        contact_id (int): FK to the contact.
        user (User): The related user object.
        contact (Contact): The related contact object.
        crisp_scores (list[CRISPScore]): Historical trust scores.
    """

    __tablename__ = "relationships"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"), nullable=False)

    user = db.relationship("User", back_populates="relationships")
    contact = db.relationship("Contact", back_populates="relationships")

    crisp_scores = db.relationship(
        "CRISPScore", back_populates="relationship", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "contact_id", name="_user_contact_uc"),
    )

    def __repr__(self) -> str:
        """Readable string representation.

        Returns:
            str: Pairing of user and contact IDs.
        """
        return f"<Relationship User={self.user_id} Contact={self.contact_id}>"