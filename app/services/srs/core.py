"""Core SRS service module for basic CRUD operations."""

from typing import Dict, Any, Optional, List
from datetime import datetime
from zoneinfo import ZoneInfo
from app.models.pages.srs import SRS, ReviewHistory
from app.services.base_service import BaseService
from app.utils.app_logging import get_logger

logger = get_logger()


class SRSCoreService(BaseService):
    """Service providing core CRUD operations for SRS items."""

    def __init__(self):
        """Initialize the SRS core service."""
        super().__init__(SRS)
        self.logger = logger
        self.logger.info("SRSCoreService: Initializing SRS core service")

    def log_review(self, srs_item_id: int, rating: int, interval: float, ease_factor: float) -> ReviewHistory:
        """
        Create a review history record.

        Args:
            srs_item_id: ID of the SRS item being reviewed
            rating: The rating given (0-5)
            interval: The calculated next interval
            ease_factor: The updated ease factor

        Returns:
            The created review history record
        """
        self.logger.info(f"SRSCoreService: Creating review history record for item {srs_item_id}")

        history = ReviewHistory(
            srs_item_id=srs_item_id,
            rating=rating,
            interval=interval,
            ease_factor=ease_factor,
        )
        history.save()

        self.logger.info(f"SRSCoreService: Logged review {history.id} for item {srs_item_id}")
        return history

    def get_review_history(self, srs_item_id: Optional[int] = None) -> List[ReviewHistory]:
        """
        Get review history, optionally filtered by SRS item ID.

        Args:
            srs_item_id: Optional ID to filter history by specific item

        Returns:
            List of review history records
        """
        self.logger.info(f"SRSCoreService: Getting review history for item {srs_item_id if srs_item_id else 'all'}")

        query = ReviewHistory.query

        if srs_item_id:
            query = query.filter(ReviewHistory.srs_item_id == srs_item_id)

        history = query.order_by(ReviewHistory.created_at.desc()).all()

        self.logger.info(f"SRSCoreService: Retrieved {len(history)} review history records")
        return history

    def get_last_review(self, srs_item_id: int) -> Optional[ReviewHistory]:
        """
        Get the most recent review for an SRS item.

        Args:
            srs_item_id: ID of the SRS item

        Returns:
            The most recent review history or None if no reviews
        """
        self.logger.info(f"SRSCoreService: Getting last review for item {srs_item_id}")

        last_review = ReviewHistory.query.filter(
            ReviewHistory.srs_item_id == srs_item_id
        ).order_by(ReviewHistory.created_at.desc()).first()

        if last_review:
            self.logger.info(f"SRSCoreService: Found last review {last_review.id} from {last_review.created_at}")
        else:
            self.logger.info(f"SRSCoreService: No review history found for item {srs_item_id}")

        return last_review

    def record_answer(self, srs_item_id: int, answer_given: str) -> None:
        """
        Record a user's answer to an SRS item.

        Args:
            srs_item_id: ID of the SRS item
            answer_given: The answer provided by the user
        """
        if not answer_given:
            return

        self.logger.info(f"SRSCoreService: Recording answer for item {srs_item_id}")

        # This is a placeholder for future functionality
        # Could store answers in a separate table or in review history
        # For now, just log that an answer was provided
        self.logger.info(f"SRSCoreService: Recorded answer of length {len(answer_given)} for item {srs_item_id}")