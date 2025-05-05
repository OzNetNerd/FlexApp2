"""Shared ORM models used across domains."""

from infrastructure.persistence.models.base import BaseModel, NotableMixin
from infrastructure.flask.extensions import db


class Note(BaseModel, NotableMixin):
    """
    ORM model for notes.

    Maps the Note domain entity to the database.
    """

    __tablename__ = "notes"

    content = db.Column(db.Text, nullable=False)
    processed_content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self) -> str:
        """Return string representation of the note."""
        return f"<Note {self.id} on {self.notable_type} {self.notable_id}>"


class Task(BaseModel, NotableMixin):
    """
    ORM model for tasks.

    Maps the Task domain entity to the database.
    """

    __tablename__ = "tasks"

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="Pending")
    priority = db.Column(db.String(20), default="Medium")
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    assigned_to = db.relationship(
        "User",
        foreign_keys=[assigned_to_id],
        backref=db.backref("assigned_tasks", lazy="dynamic")
    )

    def __repr__(self) -> str:
        """Return string representation of the task."""
        return f"<Task {self.title!r}>"


class Relationship(BaseModel):
    """
    ORM model for relationships between entities.

    Maps the Relationship domain entity to the database.
    """

    __tablename__ = "relationships"

    entity1_type = db.Column(db.String(50), nullable=False)
    entity1_id = db.Column(db.Integer, nullable=False)
    entity2_type = db.Column(db.String(50), nullable=False)
    entity2_id = db.Column(db.Integer, nullable=False)
    relationship_type = db.Column(db.String(50), nullable=False)

    # Only define relationships that are used in queries
    user = db.relationship(
        "User",
        foreign_keys="[Relationship.entity1_id]",
        primaryjoin="and_(User.id == Relationship.entity1_id, "
                    "Relationship.entity1_type == 'user')",
        back_populates="relationships",
        overlaps="contact",
    )

    contact = db.relationship(
        "Contact",
        foreign_keys="[Relationship.entity1_id]",
        primaryjoin="and_(Contact.id == Relationship.entity1_id, "
                    "Relationship.entity1_type == 'contact')",
        back_populates="relationships",
        overlaps="user",
    )

    # Relationship to CRISP scoring
    crisp = db.relationship("Crisp", back_populates="relationship", uselist=False)


class Crisp(BaseModel):
    """
    ORM model for CRISP trust metric.

    Maps the Crisp domain entity to the database.
    """

    __tablename__ = "crisp"

    relationship_id = db.Column(db.Integer, db.ForeignKey("relationships.id"), nullable=False)
    relationship = db.relationship("Relationship", back_populates="crisp")

    credibility = db.Column(db.Integer, nullable=False)
    reliability = db.Column(db.Integer, nullable=False)
    intimacy = db.Column(db.Integer, nullable=False)
    self_orientation = db.Column(db.Integer, nullable=False)

    notes = db.Column(db.Text)
    total_score = db.Column(db.Float)

    def calculate_total(self) -> None:
        """
        Calculate the CRISP total score using the standard formula.

        Sets:
            total_score: Computed float value.
        """
        c = self.credibility
        r = self.reliability
        i = self.intimacy
        s = self.self_orientation

        if s == 0:
            self.total_score = float(c + r + i)
        else:
            self.total_score = float(c + r + i) / s