"""Main SRS service module that composes specialized subservices."""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from app.models.pages.srs import SRS, ReviewHistory
from app.services.service_base import ServiceBase, ServiceRegistry
from app.services.crud_service import CRUDService
from app.services.srs.core import SRSCoreService
from app.services.srs.algorithm import SRSAlgorithmService
from app.services.srs.filters import SRSFilterService
from app.services.srs.analytics import SRSAnalyticsService
from app.services.srs.navigation import SRSNavigationService
from app.services.srs.categories import SRSCategoryService


class SRSService(CRUDService):
    """
    Service for managing SRS items and scheduling reviews based on spaced repetition principles.

    This service composes specialized subservices for different aspects of SRS functionality:
    - Core: Basic CRUD operations
    - Algorithm: Spaced repetition calculations
    - Filters: Retrieving cards with various criteria
    - Analytics: Statistics and metrics
    - Navigation: Card sequencing and positioning
    - Categories: Deck/category management
    """

    def __init__(self):
        """Initialize the SRS service."""
        super().__init__(SRS, ["title", "content"])  # Pass model class and required fields
        self.logger.info("SRSService: Initializing SRS service")

        # Initialize specialized subservices using the registry for dependency sharing
        self.core = ServiceRegistry.get(SRSCoreService)
        self.algorithm = ServiceRegistry.get(SRSAlgorithmService)
        self.filters = ServiceRegistry.get(SRSFilterService)
        self.analytics = ServiceRegistry.get(SRSAnalyticsService)
        self.navigation = ServiceRegistry.get(SRSNavigationService)
        self.categories = ServiceRegistry.get(SRSCategoryService)

    # Override inherited methods to use core service

    def get_by_id(self, item_id: int) -> Optional[SRS]:
        """Get an SRS item by ID."""
        return self.core.get_by_id(item_id)

    def get_all(self, page=1, per_page=15, sort_column="id", sort_direction="asc", filters=None) -> Union[List[SRS], Any]:
        """Get all SRS items with optional pagination."""
        if page == 1 and per_page == 15 and sort_column == "id" and not filters:
            # Use simple get_all for default parameters
            return self.core.get_all()
        # Otherwise use the inherited pagination method
        return super().get_all(page, per_page, sort_column, sort_direction, filters)

    def create(self, data: Dict[str, Any]) -> SRS:
        """Create a new SRS item."""
        return self.core.create(data)

    def update(self, item_id_or_obj: Union[int, SRS], update_data: Dict[str, Any]) -> SRS:
        """Update an SRS item."""
        return self.core.update(item_id_or_obj, update_data)

    # Rest of the class remains unchanged

    # Algorithm operations
    def preview_ratings(self, item_id: int) -> Dict[int, float]:
        """
        Preview the next intervals for each possible rating of an item.

        Args:
            item_id: ID of the SRS item

        Returns:
            Dictionary mapping UI ratings (0-5) to next intervals

        Raises:
            ValueError: If the SRS item doesn't exist
        """
        item = self.core.get_by_id(item_id)
        if not item:
            self.logger.error(f"SRSService: SRS item with ID {item_id} not found during preview_ratings")
            raise ValueError(f"SRS item with ID {item_id} not found")

        return self.algorithm.preview_ratings(item)

    def schedule_review(self, item_id: int, rating: int, answer_given: str = "") -> SRS:
        """
        Schedule the next review for an item based on the user's rating.

        Args:
            item_id: ID of the SRS item being reviewed
            rating: The UI rating given (0-5)
            answer_given: Optional answer text provided by the user

        Returns:
            The updated SRS item

        Raises:
            ValueError: If the SRS item doesn't exist
        """
        self.logger.info(f"SRSService: Scheduling review for item {item_id} with rating {rating}")

        item = self.core.get_by_id(item_id)
        if not item:
            self.logger.error(f"SRSService: SRS item with ID {item_id} not found during schedule_review")
            raise ValueError(f"SRS item with ID {item_id} not found")

        # Calculate updated values for scheduling
        update_data = self.algorithm.schedule_review(item, rating)

        # Update the item
        updated_item = self.core.update(item, update_data)

        # Record review history
        self.core.log_review(item.id, rating, update_data["interval"], update_data["ease_factor"])

        # Record answer if provided
        if answer_given:
            self.core.record_answer(item.id, answer_given)

        return updated_item

    # Filter operations
    def get_filtered_cards(self, filters: Optional[Dict[str, Any]] = None) -> List[SRS]:
        """
        Get SRS cards filtered by various criteria.

        Args:
            filters: Dictionary of filter criteria

        Returns:
            List of filtered SRS items
        """
        return self.filters.get_filtered_cards(filters)

    def get_due_items(self) -> List[SRS]:
        """
        Get all SRS items that are due for review.

        Returns:
            List of all due SRS items
        """
        return self.filters.get_due_items()

    def get_cards_by_learning_stage(self, stage: str = "new") -> List[SRS]:
        """
        Get cards filtered by their learning stage based on interval.

        Args:
            stage: One of 'new', 'learning', 'reviewing', or 'mastered'

        Returns:
            List of cards in the specified learning stage

        Raises:
            ValueError: If the stage parameter is invalid
        """
        return self.filters.get_cards_by_learning_stage(stage)

    def get_cards_by_difficulty(self, difficulty: str = "easy") -> List[SRS]:
        """
        Get cards filtered by difficulty based on ease factor.

        Args:
            difficulty: One of 'hard', 'medium', or 'easy'

        Returns:
            List of cards with the specified difficulty

        Raises:
            ValueError: If the difficulty parameter is invalid
        """
        return self.filters.get_cards_by_difficulty(difficulty)

    def get_cards_by_performance(self, performance: str = "struggling") -> List[SRS]:
        """
        Get cards filtered by user performance.

        Args:
            performance: One of 'struggling', 'average', or 'strong'

        Returns:
            List of cards that match the specified performance criteria

        Raises:
            ValueError: If the performance parameter is invalid
        """
        return self.filters.get_cards_by_performance(performance)

    def get_review_strategy(self, strategy_name: str, limit: Optional[int] = None) -> List[SRS]:
        """
        Get cards based on various predefined review strategies.

        Args:
            strategy_name: Name of the review strategy
            limit: Optional maximum number of cards to return

        Returns:
            List of cards that match the strategy criteria

        Raises:
            ValueError: If the strategy_name parameter is invalid
        """
        return self.filters.get_review_strategy(strategy_name, limit)

    def get_due_cards(self, limit: Optional[int] = None) -> List[SRS]:
        """
        Get SRS items that are due for review.

        Args:
            limit: Optional maximum number of cards to return

        Returns:
            List of SRS items due for review
        """
        return self.filters.get_due_cards(limit)

    def get_by_type(self, type_name: str) -> List[SRS]:
        """
        Get all SRS items of a specific type.

        Args:
            type_name: The notable_type to filter by

        Returns:
            List of SRS items of the specified type
        """
        return self.filters.get_cards_by_type(type_name)

    # Analytics operations
    def count_total(self) -> int:
        """
        Get the total count of SRS items.

        Returns:
            Total number of SRS items
        """
        return self.analytics.count_total()

    def count_due_today(self) -> int:
        """
        Get the count of SRS items due for review today.

        Returns:
            Number of SRS items due today
        """
        return self.analytics.count_due_today()

    def calculate_success_rate(self) -> int:
        """
        Calculate the success rate of SRS items as a percentage.

        Returns:
            Success rate as a percentage (0-100)
        """
        return self.analytics.calculate_success_rate()

    def get_stats(self) -> Dict[str, int]:
        """
        Get current SRS system statistics.

        Returns:
            Dictionary with basic statistics
        """
        return self.analytics.get_stats()

    def get_detailed_stats(self) -> Dict[str, Any]:
        """
        Get detailed learning statistics for analysis.

        Returns:
            Dictionary with comprehensive statistics about the SRS system
        """
        return self.analytics.get_detailed_stats()

    def count_reviews_today(self) -> int:
        """
        Count the number of reviews completed today.

        Returns:
            Number of reviews completed today
        """
        return self.analytics.count_reviews_today()

    def count_weekly_reviews(self) -> int:
        """
        Count the number of reviews completed in the past 7 days.

        Returns:
            Number of reviews in the past week
        """
        return self.analytics.count_weekly_reviews()

    def calculate_retention_increase(self) -> int:
        """
        Calculate the increase in retention rate over the past month compared to the previous month.

        Returns:
            Percentage point increase in retention rate (can be negative)
        """
        return self.analytics.calculate_retention_increase()

    def count_consecutive_perfect_reviews(self) -> int:
        """
        Count the number of consecutive perfect reviews (rating 4-5) in the most recent history.

        Returns:
            Number of consecutive perfect reviews
        """
        return self.analytics.count_consecutive_perfect_reviews()

    def get_learning_progress_data(self, months: int = 7) -> Dict[str, Any]:
        """
        Get historical learning progress data for charts.

        Args:
            months: Number of past months to include in the data

        Returns:
            Dictionary with labels and datasets for charting
        """
        return self.analytics.get_learning_progress_data(months)

    def count_mastered_cards_this_month(self) -> int:
        """
        Count the number of cards that became mastered this month.

        Returns:
            Number of cards that crossed the mastery threshold this month
        """
        return self.analytics.count_mastered_cards_this_month()

    def get_learning_stages_counts(self) -> Dict[str, int]:
        """
        Get counts of cards by learning stage.

        Returns:
            Dictionary with counts for each learning stage
        """
        return self.analytics.get_learning_stages_counts()

    def get_difficulty_counts(self) -> Dict[str, int]:
        """
        Get counts of cards by difficulty level.

        Returns:
            Dictionary with counts for each difficulty level
        """
        return self.analytics.get_difficulty_counts()

    def get_performance_counts(self) -> Dict[str, int]:
        """
        Get counts of cards by performance level.

        Returns:
            Dictionary with counts for each performance level
        """
        return self.analytics.get_performance_counts()

    def get_streak_days(self) -> int:
        """
        Calculate the current streak of consecutive days with SRS reviews.

        Returns:
            Number of consecutive days with at least one review
        """
        return self.analytics.get_streak_days()

    def calculate_progress_by_type(self, type_name: Optional[str] = None) -> Union[int, Dict[str, int]]:
        """
        Calculate the learning progress for cards of a specific type.

        Args:
            type_name: Optional notable_type to filter by

        Returns:
            Progress percentage (0-100) if type_name provided, or dictionary mapping types to progress
        """
        return self.analytics.calculate_progress_by_type(type_name)

    def count_due_by_type(self, type_name: Optional[str] = None) -> Union[int, Dict[str, int]]:
        """
        Count SRS items that are due for review, grouped by notable_type.

        Args:
            type_name: Optional notable_type to filter by

        Returns:
            Count if type_name provided, or dictionary mapping types to counts
        """
        return self.analytics.count_due_by_type(type_name)

    def count_by_type(self, type_name: Optional[str] = None) -> Union[int, Dict[str, int]]:
        """
        Count SRS items grouped by notable_type.

        Args:
            type_name: Optional notable_type to filter by

        Returns:
            Count if type_name provided, or dictionary mapping types to counts
        """
        return self.analytics.count_by_type(type_name)

    # Navigation operations
    def get_next_due_item_id(self, current_item_id: Optional[int] = None) -> Optional[int]:
        """
        Get the next item due for review after current_item_id.

        Args:
            current_item_id: The current item ID to find the next item after

        Returns:
            ID of the next due item, or the current item ID if no next item found
        """
        return self.navigation.get_next_due_item_id(current_item_id)

    def get_prev_item_id(self, current_item_id: int) -> int:
        """
        Get the previous item reviewed before current_item_id.

        Args:
            current_item_id: The current item ID to find the previous item before

        Returns:
            ID of the previous item, or the current item ID if no previous item found
        """
        return self.navigation.get_prev_item_id(current_item_id)

    def get_item_position(self, item_id: int) -> int:
        """
        Get the position of the item in the current review queue.

        Args:
            item_id: The ID of the item to find the position for

        Returns:
            Position of the item in the review queue (1-based)
        """
        return self.navigation.get_item_position(item_id)

    # Category operations
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get all available categories (decks).

        Returns:
            List of category objects with id, name, color, icon, and count
        """
        return self.categories.get_categories()

    def create_category(self, name: str, color: str = "secondary", icon: str = "folder") -> Dict[str, Any]:
        """
        Create a new category (deck).

        Args:
            name: The display name of the category
            color: The color code for the category
            icon: The icon name for the category

        Returns:
            Category object with id, name, color, icon, and count
        """
        return self.categories.create_category(name, color, icon)