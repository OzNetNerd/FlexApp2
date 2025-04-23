# srs_service.py

import logging
from datetime import datetime, timedelta

# Updated imports based on py-fsrs documentation
from fsrs import Scheduler, Card, Rating, ReviewLog

from app.services.crud_service import CRUDService
from app.models.srs_item import SRSItem
from app.models.review_history import ReviewHistory

logger = logging.getLogger(__name__)


class SRSService(CRUDService):
    """Manages SRSItem state and review history via FSRS."""

    def __init__(self):
        super().__init__(SRSItem)
        self.scheduler = Scheduler()  # Create the FSRS scheduler

    def preview_ratings(self, item_id: int) -> dict:
        """
        Preview what would happen with each possible rating.
        Returns a dict mapping ratings to the number of days until next review.
        """
        item = self.get_by_id(item_id)

        # Create card from current item state
        card = Card(
            due=datetime.utcnow(),
            stability=item.interval,
            difficulty=item.ease_factor,
            elapsed_days=0,  # Assuming review is happening now
            scheduled_days=item.interval,
            reps=item.repetition
        )

        # Calculate next state for each possible rating
        results = {}
        # Use all possible rating values (typically 0-4 in FSRS)
        for rating_value in range(5):  # Ratings 0-4
            rating = Rating(rating_value)
            # Get scheduling card
            next_card = self.scheduler.repeat(card, rating)
            results[rating_value] = round(next_card.scheduled_days, 1)  # Days until next review

        return results

    def schedule_review(self, item_id: int, rating: int) -> SRSItem:
        item = self.get_by_id(item_id)

        # Convert numeric rating to FSRS Rating enum
        fsrs_rating = Rating(rating)

        # Create Card from current item state
        card = Card(
            due=datetime.utcnow() if not item.next_review_at else item.next_review_at,
            stability=item.interval,
            difficulty=item.ease_factor,
            elapsed_days=0,  # Assuming review is happening now
            scheduled_days=item.interval,
            reps=item.repetition
        )

        # Get the next state using FSRS
        next_card = self.scheduler.repeat(card, fsrs_rating)

        # Calculate the next review date
        next_review_at = datetime.utcnow() + timedelta(days=next_card.scheduled_days)

        # Update item properties
        update_data = {
            'ease_factor': next_card.difficulty,
            'interval': next_card.stability,
            'repetition': item.repetition + 1,
            'review_count': item.review_count + 1,
            'next_review_at': next_review_at
        }

        # persist updated SRSItem
        logger.info(
            f"SRSService: updating item {item.id} → next in {next_card.scheduled_days:.2f}d, ef={next_card.difficulty:.2f}")
        self.update(item, update_data)  # Pass both entity and data

        # record history
        history = ReviewHistory(
            srs_item_id=item.id,
            rating=rating,
            interval=next_card.stability,
            ease_factor=next_card.difficulty,
        )
        history.save()
        logger.info(f"SRSService: logged review {history.id} for item {item.id}")

        return item

    def get_due_items(self):
        """Return all cards whose next_review_at ≤ now."""
        return SRSItem.query.filter(SRSItem.next_review_at <= datetime.utcnow()).all()