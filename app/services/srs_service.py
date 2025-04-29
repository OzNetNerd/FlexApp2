# srs_service.py - Fixed version
from datetime import UTC, datetime, timedelta
from typing import Dict, List, Optional

from app.models.pages.srs import ReviewHistory, SRS
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()

# Constants for interval calculations
MIN_INTERVAL = 1 / 144  # 10 minutes in days
SHORT_INTERVAL = 1 / 24  # 1 hour in days
MEDIUM_INTERVAL = 1 / 4  # 6 hours in days
DAY_INTERVAL = 1.0
GOOD_INITIAL_INTERVAL = 3.0  # 3 days for good initial rating
EASY_MULTIPLIER = 2.0  # Reduced from 2.5 to prevent too-sparse reviews
GOOD_MULTIPLIER = 1.5
HARD_MULTIPLIER = 1.2
DEFAULT_EASE_FACTOR = 2.0  # Starting ease factor for new cards
MIN_EASE_FACTOR = 1.3
MAX_EASE_FACTOR = 2.5
FAIL_EASE_PENALTY = 0.2
HARD_EASE_PENALTY = 0.15
EASY_EASE_BONUS = 0.1
MAX_INTERVAL = 365  # Max 1 year


class SRSService(CRUDService):
    """Service for managing SRS items and scheduling reviews based on spaced repetition principles."""

    # Map UI ratings 0-5 to FSRS/SM2 ratings 1-4
    UI_TO_FSRS_RATING = {0: 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4}

    def __init__(self):
        """Initialize the SRS service."""
        super().__init__(SRS)

    def preview_ratings(self, item_id: int) -> Dict[int, float]:
        """Preview the next intervals for each possible rating of an item."""
        item = self.get_by_id(item_id)
        if not item:
            raise ValueError(f"SRS item with ID {item_id} not found")

        results = {}
        for ui_rating in range(6):  # UI Ratings 0-5
            next_interval = self._calculate_next_interval(item, ui_rating)
            results[ui_rating] = round(next_interval, 1)

        return results

    def schedule_review(self, item_id: int, rating: int, answer_given='') -> SRS:
        """Schedule the next review for an item based on the user's rating."""
        item = self.get_by_id(item_id)
        if not item:
            raise ValueError(f"SRS item with ID {item_id} not found")

        # Set default ease factor for new cards
        if item.review_count == 0 and (item.ease_factor is None or item.ease_factor == 0):
            item.ease_factor = DEFAULT_EASE_FACTOR

        # Calculate next interval and ease factor
        next_interval = self._calculate_next_interval(item, rating)
        new_ease = self._calculate_new_ease_factor(item, rating)

        # Calculate next review date - Fixed timezone issue
        next_review_at = datetime.now(UTC) + timedelta(days=next_interval)

        # Track successful repetitions (ratings ≥ 3)
        successful_reps = item.successful_reps or 0
        if rating >= 3:
            successful_reps += 1

        # Update item properties
        update_data = {
            "ease_factor": new_ease,
            "interval": next_interval,
            "successful_reps": successful_reps,
            "review_count": (item.review_count or 0) + 1,
            "next_review_at": next_review_at,
            "last_rating": rating,
            "last_reviewed_at": datetime.now(UTC),
        }

        # Persist updated SRS
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

        if answer_given:
            # Add to history or separate table as needed
            pass

        return item

    def get_due_items(self) -> List[SRS]:
        """Get all SRS items that are due for review."""
        return SRS.query.filter(SRS.next_review_at <= datetime.now(UTC)).all()

    def _calculate_next_interval(self, item: SRS, ui_rating: int) -> float:
        """Calculate the next interval based on the rating and current item state."""
        fsrs_rating = self.UI_TO_FSRS_RATING.get(ui_rating, 1)  # Default to 1 if invalid

        # Fix: use review_count instead of repetition
        if item.review_count == 0 or item.interval <= 0:
            # Use graduated learning steps (10min → 1h → 6h → 1d)
            if fsrs_rating == 1:
                return MIN_INTERVAL  # 10 minutes
            elif fsrs_rating == 2:
                return SHORT_INTERVAL  # 1 hour
            elif fsrs_rating == 3:
                return MEDIUM_INTERVAL  # 6 hours
            else:
                return GOOD_INITIAL_INTERVAL  # 3 days
        else:
            # Apply spacing effect for reviews
            if fsrs_rating == 1:
                return SHORT_INTERVAL  # Reset to 1 hour for failed reviews
            elif fsrs_rating == 2:
                return min(item.interval * HARD_MULTIPLIER, MAX_INTERVAL)
            elif fsrs_rating == 3:
                return min(item.interval * GOOD_MULTIPLIER, MAX_INTERVAL)
            else:
                return min(item.interval * EASY_MULTIPLIER, MAX_INTERVAL)

    def _calculate_new_ease_factor(self, item: SRS, ui_rating: int) -> float:
        """Calculate the new ease factor based on the rating."""
        fsrs_rating = self.UI_TO_FSRS_RATING.get(ui_rating, 1)  # Default to 1 if invalid

        if fsrs_rating == 1:
            return max(MIN_EASE_FACTOR, item.ease_factor - FAIL_EASE_PENALTY)
        elif fsrs_rating == 2:
            return max(MIN_EASE_FACTOR, item.ease_factor - HARD_EASE_PENALTY)
        elif fsrs_rating == 3:
            return item.ease_factor  # No change
        else:
            return min(MAX_EASE_FACTOR, item.ease_factor + EASY_EASE_BONUS)

    def get_next_due_item_id(self, current_item_id=None):
        """Get the next item due for review after current_item_id."""
        query = SRS.query.filter(SRS.next_review_at <= datetime.now(UTC))

        if current_item_id:
            # Try to find the next item in sequence
            next_items = query.filter(SRS.id > current_item_id).order_by(SRS.id).limit(1).all()
            if next_items:
                return next_items[0].id

        # Otherwise get the first due item
        first_item = query.order_by(SRS.next_review_at).first()
        return first_item.id if first_item else current_item_id

    def get_prev_item_id(self, current_item_id):
        """Get the previous item reviewed before current_item_id."""
        prev_items = SRS.query.filter(SRS.id < current_item_id).order_by(SRS.id.desc()).limit(1).all()
        return prev_items[0].id if prev_items else current_item_id

    def get_item_position(self, item_id):
        """Get the position of the item in the current review queue."""
        item = self.get_by_id(item_id)
        if not item:
            return 1

        # Count items before this one
        position = SRS.query.filter(
            SRS.next_review_at <= item.next_review_at,
            SRS.id <= item_id
        ).count()

        return position

    def get_stats(self):
        """Get current SRS system statistics."""
        total = SRS.query.count()
        due_today = SRS.query.filter(
            SRS.next_review_at <= datetime.now(UTC)
        ).count()

        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        reviewed_today = ReviewHistory.query.filter(
            ReviewHistory.timestamp >= today_start
        ).count()

        return {
            'total_cards': total,
            'cards_due': due_today,
            'cards_reviewed_today': reviewed_today
        }