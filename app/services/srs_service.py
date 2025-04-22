# srs_service.py

import logging
from datetime import datetime, timedelta

import fsrs
from fsrs import FSRS, Card

from app.services.crud_service import CRUDService
from app.models.srs_item import SRSItem
from app.models.review_history import ReviewHistory

logger = logging.getLogger(__name__)


class SRSService(CRUDService):
    """Manages SRSItem state and review history via FSRS."""

    def __init__(self):
        super().__init__(SRSItem)
        self.fsrs = FSRS()  # Create FSRS instance

    def schedule_review(self, item_id: int, rating: int) -> SRSItem:
        item = self.get_by_id(item_id)

        # Create an FSRS Card with the current state
        card = Card(
            due=datetime.utcnow(),
            stability=item.interval,
            difficulty=item.ease_factor,
            reps=item.repetition
        )

        # Get the updated card using FSRS
        new_card = self.fsrs.repeat(card, rating)

        # Update item properties
        item.ease_factor = new_card.difficulty
        item.interval = new_card.stability
        item.repetition = new_card.reps
        item.review_count += 1
        item.next_review_at = datetime.utcnow() + timedelta(days=new_card.stability)

        # Create update data dictionary for CRUDService.update()
        update_data = {
            'ease_factor': new_card.difficulty,
            'interval': new_card.stability,
            'repetition': new_card.reps,
            'review_count': item.review_count,
            'next_review_at': item.next_review_at
        }

        # persist updated SRSItem
        logger.info(f"SRSService: updating item {item.id} → next in {new_card.stability:.2f}d, ef={new_card.difficulty:.2f}")
        self.update(item, update_data)  # Pass both entity and data

        # record history
        history = ReviewHistory(
            srs_item_id=item.id,
            rating=rating,
            interval=new_card.stability,
            ease_factor=new_card.difficulty,
        )
        history.save()
        logger.info(f"SRSService: logged review {history.id} for item {item.id}")

        return item

    def get_due_items(self):
        """Return all cards whose next_review_at ≤ now."""
        return SRSItem.query.filter(SRSItem.next_review_at <= datetime.utcnow()).all()