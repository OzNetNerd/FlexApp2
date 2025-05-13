"""Algorithm service for SRS spacing calculations."""

from typing import Dict, Any
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.models.pages.srs import SRS
from app.services.service_base import ServiceBase
from app.services.srs.constants import (
    MIN_INTERVAL,
    SHORT_INTERVAL,
    MEDIUM_INTERVAL,
    GOOD_INITIAL_INTERVAL,
    EASY_MULTIPLIER,
    GOOD_MULTIPLIER,
    HARD_MULTIPLIER,
    DEFAULT_EASE_FACTOR,
    MIN_EASE_FACTOR,
    MAX_EASE_FACTOR,
    FAIL_EASE_PENALTY,
    HARD_EASE_PENALTY,
    EASY_EASE_BONUS,
    MAX_INTERVAL,
    UI_TO_FSRS_RATING,
)


class SRSAlgorithmService(ServiceBase):
    """Service for spaced repetition algorithm calculations."""

    def calculate_next_interval(self, item: SRS, ui_rating: int) -> float:
        """
        Calculate the next interval based on the rating and current item state.

        Args:
            item: SRS item being reviewed
            ui_rating: UI rating (0-5)

        Returns:
            Next interval in days
        """
        self.logger.info(f"SRSAlgorithmService: Calculating next interval for item {item.id} with UI rating {ui_rating}")
        fsrs_rating = UI_TO_FSRS_RATING.get(ui_rating, 1)  # Default to 1 if invalid
        self.logger.info(f"SRSAlgorithmService: Mapped UI rating {ui_rating} to FSRS rating {fsrs_rating}")

        # New card or invalid interval handling
        if item.review_count == 0 or item.interval <= 0:
            self.logger.info(f"SRSAlgorithmService: Item {item.id} is new or has invalid interval, applying initial learning steps")
            # Use graduated learning steps (10min → 1h → 6h → 1d)
            if fsrs_rating == 1:
                interval = MIN_INTERVAL  # 10 minutes
                self.logger.info(f"SRSAlgorithmService: Rating 1 (Again) - setting interval to {interval:.4f} days (10 min)")
                return interval
            elif fsrs_rating == 2:
                interval = SHORT_INTERVAL  # 1 hour
                self.logger.info(f"SRSAlgorithmService: Rating 2 (Hard) - setting interval to {interval:.4f} days (1 hour)")
                return interval
            elif fsrs_rating == 3:
                interval = MEDIUM_INTERVAL  # 6 hours
                self.logger.info(f"SRSAlgorithmService: Rating 3 (Good) - setting interval to {interval:.4f} days (6 hours)")
                return interval
            else:
                interval = GOOD_INITIAL_INTERVAL  # 3 days
                self.logger.info(f"SRSAlgorithmService: Rating 4 (Easy) - setting interval to {interval:.1f} days")
                return interval
        else:
            self.logger.info(f"SRSAlgorithmService: Item {item.id} is in review phase, applying spacing effect")
            # Apply spacing effect for reviews
            if fsrs_rating == 1:
                interval = SHORT_INTERVAL  # Reset to 1 hour for failed reviews
                self.logger.info(f"SRSAlgorithmService: Rating 1 (Again) - resetting interval to {interval:.4f} days (1 hour)")
                return interval
            elif fsrs_rating == 2:
                interval = min(item.interval * HARD_MULTIPLIER, MAX_INTERVAL)
                self.logger.info(f"SRSAlgorithmService: Rating 2 (Hard) - setting interval to {interval:.2f} days (x{HARD_MULTIPLIER})")
                return interval
            elif fsrs_rating == 3:
                interval = min(item.interval * GOOD_MULTIPLIER, MAX_INTERVAL)
                self.logger.info(f"SRSAlgorithmService: Rating 3 (Good) - setting interval to {interval:.2f} days (x{GOOD_MULTIPLIER})")
                return interval
            else:
                interval = min(item.interval * EASY_MULTIPLIER, MAX_INTERVAL)
                self.logger.info(f"SRSAlgorithmService: Rating 4 (Easy) - setting interval to {interval:.2f} days (x{EASY_MULTIPLIER})")
                return interval

    def calculate_new_ease_factor(self, item: SRS, ui_rating: int) -> float:
        """
        Calculate the new ease factor based on the rating.

        Args:
            item: SRS item being reviewed
            ui_rating: UI rating (0-5)

        Returns:
            New ease factor
        """
        self.logger.info(f"SRSAlgorithmService: Calculating new ease factor for item {item.id} with UI rating {ui_rating}")
        fsrs_rating = UI_TO_FSRS_RATING.get(ui_rating, 1)  # Default to 1 if invalid
        current_ease = item.ease_factor or DEFAULT_EASE_FACTOR
        self.logger.info(f"SRSAlgorithmService: Current ease factor: {current_ease:.2f}")

        if fsrs_rating == 1:
            new_ease = max(MIN_EASE_FACTOR, current_ease - FAIL_EASE_PENALTY)
            self.logger.info(f"SRSAlgorithmService: Rating 1 (Again) - reducing ease by {FAIL_EASE_PENALTY} to {new_ease:.2f}")
            return new_ease
        elif fsrs_rating == 2:
            new_ease = max(MIN_EASE_FACTOR, current_ease - HARD_EASE_PENALTY)
            self.logger.info(f"SRSAlgorithmService: Rating 2 (Hard) - reducing ease by {HARD_EASE_PENALTY} to {new_ease:.2f}")
            return new_ease
        elif fsrs_rating == 3:
            self.logger.info(f"SRSAlgorithmService: Rating 3 (Good) - keeping ease at {current_ease:.2f}")
            return current_ease  # No change
        else:
            new_ease = min(MAX_EASE_FACTOR, current_ease + EASY_EASE_BONUS)
            self.logger.info(f"SRSAlgorithmService: Rating 4 (Easy) - increasing ease by {EASY_EASE_BONUS} to {new_ease:.2f}")
            return new_ease

    def preview_ratings(self, item: SRS) -> Dict[int, float]:
        """
        Preview the next intervals for each possible rating of an item.

        Args:
            item: SRS item to preview ratings for

        Returns:
            Dictionary mapping UI ratings (0-5) to next intervals
        """
        self.logger.info(f"SRSAlgorithmService: Previewing intervals for all ratings for item {item.id}")

        results = {}
        for ui_rating in range(6):  # UI Ratings 0-5
            next_interval = self.calculate_next_interval(item, ui_rating)
            results[ui_rating] = round(next_interval, 1)

        self.logger.info(f"SRSAlgorithmService: Interval previews for item {item.id}: {results}")
        return results

    def calculate_next_review_date(self, interval: float) -> datetime:
        """
        Calculate the next review date based on an interval.

        Args:
            interval: Interval in days

        Returns:
            Next review date in UTC
        """
        self.logger.info(f"SRSAlgorithmService: Calculating next review date for interval {interval:.2f} days")
        next_review_at = datetime.now(ZoneInfo("UTC")) + timedelta(days=interval)
        self.logger.info(f"SRSAlgorithmService: Next review scheduled for {next_review_at.isoformat()}")
        return next_review_at

    def schedule_review(self, item: SRS, rating: int) -> Dict[str, Any]:
        """
        Calculate updated values for scheduling the next review.

        Args:
            item: SRS item being reviewed
            rating: UI rating (0-5)

        Returns:
            Dictionary with updated values for the item
        """
        self.logger.info(f"SRSAlgorithmService: Scheduling review for item {item.id} with rating {rating}")

        # Set default ease factor for new cards
        if item.review_count == 0 and (item.ease_factor is None or item.ease_factor == 0):
            self.logger.info(f"SRSAlgorithmService: Setting default ease factor for new item {item.id}")
            item.ease_factor = DEFAULT_EASE_FACTOR

        # Calculate next interval and ease factor
        next_interval = self.calculate_next_interval(item, rating)
        new_ease = self.calculate_new_ease_factor(item, rating)
        self.logger.info(f"SRSAlgorithmService: Calculated next interval: {next_interval:.2f} days, new ease factor: {new_ease:.2f}")

        # Calculate next review date
        next_review_at = self.calculate_next_review_date(next_interval)

        # Track successful repetitions (ratings ≥ 3)
        successful_reps = item.successful_reps or 0
        if rating >= 3:
            successful_reps += 1
            self.logger.info(f"SRSAlgorithmService: Incrementing successful repetitions to {successful_reps}")

        # Build update data
        update_data = {
            "ease_factor": new_ease,
            "interval": next_interval,
            "successful_reps": successful_reps,
            "review_count": (item.review_count or 0) + 1,
            "next_review_at": next_review_at,
            "last_rating": rating,
            "last_reviewed_at": datetime.now(ZoneInfo("UTC")),
        }

        self.logger.info(f"SRSAlgorithmService: Prepared update data for item {item.id} → next in {next_interval:.2f}d, ef={new_ease:.2f}")
        return update_data
