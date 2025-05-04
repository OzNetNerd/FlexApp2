# app/models/srs.py

from app.models.base import BaseModel, db
from app.models.mixins import NotableMixin, TimezoneMixin
from sqlalchemy.orm import relationship


class SRS(BaseModel, NotableMixin, TimezoneMixin):
    """
    SRS model for spaced repetition learning cards.

    This model stores question-answer pairs linked to entities in the CRM
    (contacts, companies, opportunities) and tracks learning state including
    review intervals, ease factors, and success rates.
    """

    __tablename__ = "srs"

    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

    # Use timezone=True to store timezone information
    next_review_at = db.Column(db.DateTime(timezone=True))
    last_reviewed_at = db.Column(db.DateTime(timezone=True))

    # SRS algorithm fields
    interval = db.Column(db.Float, default=0)
    ease_factor = db.Column(db.Float, default=2.5)
    review_count = db.Column(db.Integer, default=0)
    successful_reps = db.Column(db.Integer, default=0)
    last_rating = db.Column(db.Integer)

    # Relationship to review history
    review_history = relationship("ReviewHistory", back_populates="srs_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SRS id={self.id} q='{self.question[:20]}...'>"

    def to_dict(self):
        """Convert SRS item to dictionary."""
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "notable_type": self.notable_type,
            "notable_id": self.notable_id,
            "interval": self.interval,
            "ease_factor": self.ease_factor,
            "review_count": self.review_count,
            "successful_reps": self.successful_reps,
            "next_review_at": self.next_review_at.isoformat() if self.next_review_at else None,
            "last_reviewed_at": self.last_reviewed_at.isoformat() if self.last_reviewed_at else None,
            "last_rating": self.last_rating,
        }


class ReviewHistory(BaseModel, TimezoneMixin):
    """
    Stores the history of SRS card reviews.

    Each review includes the rating given, resulting interval,
    and timestamp for analysis and future algorithm improvements.
    """

    __tablename__ = "review_history"

    srs_item_id = db.Column(db.Integer, db.ForeignKey("srs.id"))
    rating = db.Column(db.Integer)
    interval = db.Column(db.Float)
    ease_factor = db.Column(db.Float)

    # Relationship to SRS item
    srs_item = relationship("SRS", back_populates="review_history")