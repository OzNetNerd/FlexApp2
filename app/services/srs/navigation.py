"""Navigation service for SRS item positioning and sequencing."""

from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from app.models.pages.srs import SRS
from app.utils.app_logging import get_logger

logger = get_logger()


class SRSNavigationService:
    """Service for navigating between SRS items during review sessions."""

    def __init__(self):
        """Initialize the SRS navigation service."""
        self.logger = logger
        self.logger.info("SRSNavigationService: Initializing SRS navigation service")

    def get_next_due_item_id(self, current_item_id: Optional[int] = None) -> Optional[int]:
        """
        Get the next item due for review after current_item_id.

        Args:
            current_item_id: The current item ID to find the next item after

        Returns:
            ID of the next due item, or the current item ID if no next item found
        """
        self.logger.info(f"SRSNavigationService: Finding next due item after item ID {current_item_id}")
        query = SRS.query.filter(
            SRS.next_review_at.isnot(None),
            SRS.next_review_at <= datetime.now(ZoneInfo("UTC"))
        )

        if current_item_id:
            # Try to find the next item in sequence
            self.logger.info(f"SRSNavigationService: Searching for items with ID > {current_item_id}")
            next_items = query.filter(SRS.id > current_item_id).order_by(SRS.id).limit(1).all()
            if next_items:
                self.logger.info(f"SRSNavigationService: Found next due item: {next_items[0].id}")
                return next_items[0].id

        # Otherwise get the first due item
        self.logger.info("SRSNavigationService: No next item found, retrieving first due item")
        first_item = query.order_by(SRS.next_review_at).first()
        result_id = first_item.id if first_item else current_item_id
        self.logger.info(f"SRSNavigationService: Returning item ID: {result_id}")
        return result_id

    def get_prev_item_id(self, current_item_id: int) -> int:
        """
        Get the previous item reviewed before current_item_id.

        Args:
            current_item_id: The current item ID to find the previous item before

        Returns:
            ID of the previous item, or the current item ID if no previous item found
        """
        self.logger.info(f"SRSNavigationService: Finding previous item before item ID {current_item_id}")
        prev_items = SRS.query.filter(SRS.id < current_item_id).order_by(SRS.id.desc()).limit(1).all()
        result_id = prev_items[0].id if prev_items else current_item_id
        self.logger.info(f"SRSNavigationService: Returning previous item ID: {result_id}")
        return result_id

    def get_item_position(self, item_id: int) -> int:
        """
        Get the position of the item in the current review queue.

        Args:
            item_id: The ID of the item to find the position for

        Returns:
            Position of the item in the review queue (1-based)
        """
        self.logger.info(f"SRSNavigationService: Calculating position of item {item_id} in review queue")
        item = SRS.query.get(item_id)
        if not item:
            self.logger.info(f"SRSNavigationService: Item {item_id} not found, returning position 1")
            return 1

        # Count items before this one
        position = SRS.query.filter(
            SRS.next_review_at <= item.next_review_at,
            SRS.id <= item_id
        ).count()

        self.logger.info(f"SRSNavigationService: Item {item_id} is at position {position} in review queue")
        return position

    def get_next_in_category(self, item_id: int, category: str) -> Optional[int]:
        """
        Get the next item in the same category.

        Args:
            item_id: The current item ID
            category: The category/notable_type to filter by

        Returns:
            ID of the next item in the category, or None if not found
        """
        self.logger.info(f"SRSNavigationService: Finding next item in category '{category}' after item {item_id}")
        next_item = SRS.query.filter(
            SRS.notable_type == category,
            SRS.id > item_id
        ).order_by(SRS.id).first()

        if next_item:
            self.logger.info(f"SRSNavigationService: Found next item {next_item.id} in category '{category}'")
            return next_item.id
        else:
            self.logger.info(f"SRSNavigationService: No more items in category '{category}' after item {item_id}")
            return None

    def get_first_in_category(self, category: str) -> Optional[int]:
        """
        Get the first item in a category.

        Args:
            category: The category/notable_type to filter by

        Returns:
            ID of the first item in the category, or None if category empty
        """
        self.logger.info(f"SRSNavigationService: Finding first item in category '{category}'")
        first_item = SRS.query.filter(
            SRS.notable_type == category
        ).order_by(SRS.id).first()

        if first_item:
            self.logger.info(f"SRSNavigationService: Found first item {first_item.id} in category '{category}'")
            return first_item.id
        else:
            self.logger.info(f"SRSNavigationService: No items found in category '{category}'")
            return None

    def get_queue_length(self) -> int:
        """
        Get the total number of items due for review.

        Returns:
            Number of items in the current review queue
        """
        self.logger.info("SRSNavigationService: Getting total number of items due for review")
        count = SRS.query.filter(
            SRS.next_review_at.isnot(None),
            SRS.next_review_at <= datetime.now(ZoneInfo("UTC"))
        ).count()

        self.logger.info(f"SRSNavigationService: Found {count} items due for review")
        return count

    def get_remaining_count(self, current_item_id: int) -> int:
        """
        Get the number of items remaining in the review queue after the current item.

        Args:
            current_item_id: The current item ID

        Returns:
            Number of remaining items to review
        """
        self.logger.info(f"SRSNavigationService: Calculating remaining items after item {current_item_id}")
        current_item = SRS.query.get(current_item_id)

        if not current_item:
            self.logger.info(f"SRSNavigationService: Item {current_item_id} not found, returning total queue length")
            return self.get_queue_length()

        # Count items after this one based on due date and ID
        count = SRS.query.filter(
            SRS.next_review_at.isnot(None),
            SRS.next_review_at <= datetime.now(ZoneInfo("UTC")),
            SRS.next_review_at > current_item.next_review_at
        ).count()

        # Add items with same due date but higher ID
        count += SRS.query.filter(
            SRS.next_review_at == current_item.next_review_at,
            SRS.id > current_item_id
        ).count()

        self.logger.info(f"SRSNavigationService: {count} items remaining after item {current_item_id}")
        return count