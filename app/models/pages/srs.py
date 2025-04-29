# srs.py

from datetime import datetime
from app.models.base import BaseModel, db


class SRSItem(BaseModel):
    """
    Represents an SRS item for spaced repetition review.
    """

    __tablename__ = "srs_items"
    __entity_name__ = "SRSItem"  # Add this line

    id = db.Column(db.Integer, primary_key=True)

    notable_type = db.Column(db.String(50), nullable=False)
    notable_id = db.Column(db.Integer, nullable=False)

    # front/back payload
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

    # FSRS state
    repetition = db.Column(db.Integer, default=0, nullable=False)
    interval = db.Column(db.Float, default=0.0, nullable=False)  # in days
    ease_factor = db.Column(db.Float, default=2.5, nullable=False)
    review_count = db.Column(db.Integer, default=0, nullable=False)

    next_review_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SRSItem {self.id} [{self.notable_type}: {self.notable_id}] next={self.next_review_at}>"


class ReviewHistory(BaseModel):
    """
    Records the review history entries for SRS items.
    """

    __tablename__ = "review_history"

    id = db.Column(db.Integer, primary_key=True)

    srs_item_id = db.Column(db.Integer, db.ForeignKey("srs_items.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.Float, nullable=False)
    ease_factor = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<ReviewHistory item={self.srs_item_id} rating={self.rating} at={self.timestamp}>"
