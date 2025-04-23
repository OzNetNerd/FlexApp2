# review_history.py
from datetime import datetime

from app.models.base import BaseModel, db


class ReviewHistory(BaseModel):
    __tablename__ = "review_history"

    # Add primary key
    id = db.Column(db.Integer, primary_key=True)

    srs_item_id = db.Column(db.Integer, db.ForeignKey("srs_items.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.Float, nullable=False)
    ease_factor = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<ReviewHistory item={self.srs_item_id} rating={self.rating} at={self.timestamp}>"
