from datetime import UTC, datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import db, BaseModel


class SRS(BaseModel):
    """
    SRS model for spaced repetition learning cards.

    This model stores question-answer pairs linked to entities in the CRM
    (contacts, companies, opportunities) and tracks learning state including
    review intervals, ease factors, and success rates.
    """
    __tablename__ = 'srs'

    id = Column(Integer, primary_key=True)

    # Card content
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    # Entity reference (polymorphic relationship)
    notable_type = Column(String(50), nullable=False)
    notable_id = Column(Integer, nullable=False)

    # SRS algorithm state
    interval = Column(Float, default=0)  # Current interval in days
    ease_factor = Column(Float, default=2.0)  # Current ease factor (SM-2 algorithm)
    review_count = Column(Integer, default=0)  # Number of times reviewed
    successful_reps = Column(Integer, default=0)  # Number of successful reviews (rating >= 3)

    # Review timestamps
    next_review_at = Column(DateTime(timezone=True), default=datetime.now(UTC))
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Last review data
    last_rating = Column(Integer, nullable=True)  # Last rating given (0-5)

    # Relationship to review history
    review_history = relationship("ReviewHistory", back_populates="srs_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SRS id={self.id} q='{self.question[:20]}...'>"

    def to_dict(self):
        """Convert SRS item to dictionary."""
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'notable_type': self.notable_type,
            'notable_id': self.notable_id,
            'interval': self.interval,
            'ease_factor': self.ease_factor,
            'review_count': self.review_count,
            'successful_reps': self.successful_reps,
            'next_review_at': self.next_review_at.isoformat() if self.next_review_at else None,
            'last_reviewed_at': self.last_reviewed_at.isoformat() if self.last_reviewed_at else None,
            'last_rating': self.last_rating
        }


class ReviewHistory(BaseModel):
    """
    Stores the history of SRS card reviews.

    Each review includes the rating given, resulting interval,
    and timestamp for analysis and future algorithm improvements.
    """
    __tablename__ = 'review_history'

    id = Column(Integer, primary_key=True)
    srs_item_id = Column(Integer, ForeignKey('srs.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # Rating given (0-5)
    interval = Column(Float, nullable=False)  # Resulting interval in days
    ease_factor = Column(Float, nullable=False)  # Resulting ease factor
    timestamp = Column(DateTime(timezone=True), default=datetime.now(UTC))

    # Relationship to SRS item
    srs_item = relationship("SRS", back_populates="review_history")

    def save(self):
        """Save the review history to the database."""
        db.session.add(self)
        db.session.commit()