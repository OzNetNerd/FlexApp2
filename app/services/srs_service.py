# srs_service.py

import logging
from datetime import datetime, timedelta

import fsrs

from app.services.crud_service import CRUDService
from app.models.srs_item import SRSItem
from app.models.review_history import ReviewHistory

logger = logging.getLogger(__name__)


class SRSService(CRUDService):
    """Manages SRSItem state and review history via FSRS."""

    def __init__(self):
        super().__init__(SRSItem)

    def schedule_review(self, item_id: int, rating: int) -> SRSItem:
        item = self.get_by_id(item_id)

        # FSRS step: (new_ease, new_interval_days, new_repetition)
        new_ease, new_interval, new_repetition = fsrs.srs1.step(
            rating,
            item.repetition,
            item.interval,
            item.ease_factor,
        )

        item.ease_factor = new_ease
        item.interval = new_interval
        item.repetition = new_repetition
        item.review_count += 1
        item.next_review_at = datetime.utcnow() + timedelta(days=new_interval)

        # persist updated SRSItem
        logger.info(f"SRSService: updating item {item.id} → next in {new_interval}d, ef={new_ease:.2f}")
        self.update(item)

        # record history
        history = ReviewHistory(
            srs_item_id=item.id,
            rating=rating,
            interval=new_interval,
            ease_factor=new_ease,
        )
        history.save()
        logger.info(f"SRSService: logged review {history.id} for item {item.id}")

        return item

    def get_due_items(self):
        """Return all cards whose next_review_at ≤ now."""
        return SRSItem.query.filter(SRSItem.next_review_at <= datetime.utcnow()).all()
