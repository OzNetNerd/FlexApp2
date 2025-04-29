# srs.py

from datetime import datetime, timezone
from app.models.base import BaseModel, db
from sqlalchemy import Index


class SRSItem(BaseModel):
    """
    Represents an SRS item for spaced repetition review.

    Attributes:
        id: Primary key
        notable_type/notable_id: Reference to the associated content item
        question/answer: Content of the flashcard
        successful_reps: Counter for successful reviews (ratings ≥ 3)
        review_count: Total number of reviews regardless of rating
        last_rating: Most recent rating (0-5) given to this item
        interval: Current interval in days between reviews
        ease_factor: Difficulty factor affecting interval growth
        next_review_at: DateTime when the item is due for review
        last_reviewed_at: DateTime when the item was last reviewed
    """

    __tablename__ = "srs_items"
    __entity_name__ = "SRSItem"

    id = db.Column(db.Integer, primary_key=True)

    # Reference to the associated item
    notable_type = db.Column(db.String(50), nullable=False)
    notable_id = db.Column(db.Integer, nullable=False)

    # Card content
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

    # SRS algorithm state
    successful_reps = db.Column(db.Integer, default=0, nullable=False,
                                comment="Count of successful repetitions (rating ≥ 3)")
    review_count = db.Column(db.Integer, default=0, nullable=False,
                             comment="Total review count regardless of rating")
    last_rating = db.Column(db.Integer, nullable=True,
                            comment="Most recent rating (0-5)")

    interval = db.Column(db.Float, default=0.0, nullable=False,
                         comment="Current interval in days")
    ease_factor = db.Column(db.Float, default=2.0, nullable=False,
                            comment="Difficulty factor (1.3-2.5)")

    # Timing
    next_review_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc),
                               nullable=False, index=True)
    last_reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Create composite index for finding cards by notable reference
    __table_args__ = (
        Index('idx_srs_items_notable', 'notable_type', 'notable_id'),
    )

    def __repr__(self):
        return f"<SRSItem {self.id} [{self.notable_type}: {self.notable_id}] next={self.next_review_at}>"


class ReviewHistory(BaseModel):
    """
    Records the review history for SRS items.

    Attributes:
        id: Primary key
        srs_item_id: Foreign key to the related SRS item
        timestamp: When the review occurred
        rating: Rating given during review (0-5)
        interval: Interval that was set after this review
        ease_factor: Ease factor after this review
    """

    __tablename__ = "review_history"

    id = db.Column(db.Integer, primary_key=True)
    srs_item_id = db.Column(db.Integer, db.ForeignKey("srs_items.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc),
                          nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.Float, nullable=False)
    ease_factor = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<ReviewHistory item={self.srs_item_id} rating={self.rating} at={self.timestamp}>"