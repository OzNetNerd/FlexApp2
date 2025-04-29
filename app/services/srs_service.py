# srs_service.py

from datetime import UTC, datetime, timedelta

# Updated imports based on py-fsrs documentation
from fsrs import Scheduler

from app.models.pages.srs import ReviewHistory, SRSItem
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()


class SRSService(CRUDService):
    """Manages SRSItem state and review history via FSRS."""

    def __init__(self):
        super().__init__(SRSItem)
        self.scheduler = Scheduler()  # Create the FSRS scheduler

    def preview_ratings(self, item_id: int) -> dict:
        """Preview what would happen with each possible rating."""
        item = self.get_by_id(item_id)

        # Map UI ratings 0-5 to FSRS ratings 1-4
        ui_to_fsrs_mapping = {0: 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4}
        results = {}

        for ui_rating in range(6):  # UI Ratings 0-5
            fsrs_rating = ui_to_fsrs_mapping[ui_rating]

            # Calculate next interval based on the rating
            # For a new card or when there's no stability yet
            if item.repetition == 0 or item.interval <= 0:
                # Use learning steps for first few ratings
                if fsrs_rating <= 2:
                    days = 1 / 24  # 1 hour
                elif fsrs_rating == 3:
                    days = 1  # 1 day
                else:
                    days = 4  # 4 days
            else:
                # Apply spacing effect for reviews
                if fsrs_rating == 1:
                    days = 1  # 1 day
                elif fsrs_rating == 2:
                    days = item.interval * 1.2
                elif fsrs_rating == 3:
                    days = item.interval * 1.5
                else:
                    days = item.interval * 2.5

            results[ui_rating] = round(days, 1)

        return results

    def schedule_review(self, item_id: int, rating: int) -> SRSItem:
        item = self.get_by_id(item_id)

        # Map UI rating to FSRS rating (FSRS uses 1-4)
        ui_to_fsrs_mapping = {0: 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4}
        fsrs_rating_value = ui_to_fsrs_mapping.get(rating, 1)  # Default to 1 if invalid

        # Calculate next interval based on the rating
        # For a new card or when there's no stability yet
        if item.repetition == 0 or item.interval <= 0:
            # Use learning steps for first few ratings
            if fsrs_rating_value <= 2:
                next_interval = 1 / 24  # 1 hour
                new_ease = max(1.3, item.ease_factor - 0.2)
            elif fsrs_rating_value == 3:
                next_interval = 1  # 1 day
                new_ease = item.ease_factor
            else:
                next_interval = 4  # 4 days
                new_ease = min(2.5, item.ease_factor + 0.1)
        else:
            # Apply spacing effect for reviews
            if fsrs_rating_value == 1:
                next_interval = 1  # 1 day
                new_ease = max(1.3, item.ease_factor - 0.2)
            elif fsrs_rating_value == 2:
                next_interval = item.interval * 1.2
                new_ease = max(1.3, item.ease_factor - 0.15)
            elif fsrs_rating_value == 3:
                next_interval = item.interval * 1.5
                new_ease = item.ease_factor
            else:
                next_interval = item.interval * 2.5
                new_ease = min(2.5, item.ease_factor + 0.1)

        # Limit maximum interval
        next_interval = min(next_interval, 365)  # Max 1 year

        # Calculate next review date
        next_review_at = datetime.now(UTC) + timedelta(days=next_interval)

        # Update item properties
        update_data = {
            "ease_factor": new_ease,
            "interval": next_interval,
            "repetition": item.repetition + 1,
            "review_count": item.review_count + 1,
            "next_review_at": next_review_at,
        }

        # Persist updated SRSItem
        logger.info(f"SRSService: updating item {item.id} → next in {next_interval:.2f}d, ef={new_ease:.2f}")
        self.update(item, update_data)

        # Record history
        history = ReviewHistory(
            srs_item_id=item.id,
            rating=rating,
            interval=next_interval,
            ease_factor=new_ease,
        )
        history.save()
        logger.info(f"SRSService: logged review {history.id} for item {item.id}")

        return item

    @staticmethod
    def get_due_items():
        """Return all cards whose next_review_at ≤ now."""
        return SRSItem.query.filter(SRSItem.next_review_at <= datetime.now(UTC)).all()
