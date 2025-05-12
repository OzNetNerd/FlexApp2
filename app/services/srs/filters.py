"""Filter service for retrieving SRS items based on various criteria."""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import func
from app.models.pages.srs import SRS, ReviewHistory
from app.services.service_base import QueryService
from app.services.srs.constants import (
    LEARNING_THRESHOLD, REVIEWING_THRESHOLD, HARD_THRESHOLD,
    MEDIUM_THRESHOLD, STRUGGLING_THRESHOLD, AVERAGE_THRESHOLD
)

class SRSFilterService(QueryService):
    """Service for filtering and retrieving SRS items based on various criteria."""

    def __init__(self):
        """Initialize the SRS filter service."""
        super().__init__(SRS)

    def get_filtered_cards(self, filters: Optional[Dict[str, Any]] = None) -> List[SRS]:
        """
        Get SRS cards filtered by various criteria.

        Args:
            filters: Dictionary of filter criteria including:
                    - due_only: Only include cards due for review
                    - category/notable_type: Filter by card category
                    - search: Text search in card content
                    - min_interval/max_interval: Filter by interval range
                    - min_ease/max_ease: Filter by ease factor range
                    - sort_by/sort_order: Sorting parameters

        Returns:
            List of filtered SRS items
        """
        self.logger.info(f"SRSFilterService: Getting filtered cards with filters: {filters}")

        # Start with base query
        query = SRS.query

        # Apply filters if provided
        if filters:
            # Due cards filter
            if filters.get("due_only"):
                self.logger.info("SRSFilterService: Applying due_only filter")
                query = query.filter(
                    SRS.next_review_at.isnot(None),
                    SRS.next_review_at <= datetime.now(ZoneInfo("UTC"))
                )

            # Category filter
            if filters.get("category"):
                self.logger.info(f"SRSFilterService: Applying category filter: {filters['category']}")
                query = query.filter(SRS.notable_type == filters["category"])

            # Text search in question or answer
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                self.logger.info(f"SRSFilterService: Applying search filter: {filters['search']}")
                query = query.filter(
                    (SRS.question.ilike(search_term)) | (SRS.answer.ilike(search_term))
                )

            # Interval range
            query = self.apply_numeric_range(
                query,
                SRS.interval,
                filters.get("min_interval"),
                filters.get("max_interval")
            )

            # Ease factor range
            query = self.apply_numeric_range(
                query,
                SRS.ease_factor,
                filters.get("min_ease"),
                filters.get("max_ease")
            )

            # Sort order
            query = self.apply_sort(
                query,
                filters.get("sort_by", "next_review_at"),
                filters.get("sort_order", "asc")
            )

        # Execute query
        result = query.all()
        self.logger.info(f"SRSFilterService: Filtered query returned {len(result)} cards")
        return result

    def get_due_items(self) -> List[SRS]:
        """
        Get all SRS items that are due for review.

        Returns:
            List of all due SRS items
        """
        self.logger.info("SRSFilterService: Retrieving all due SRS items")
        items = SRS.query.filter(
            SRS.next_review_at.isnot(None),
            SRS.next_review_at <= datetime.now(ZoneInfo("UTC"))
        ).all()

        self.logger.info(f"SRSFilterService: Found {len(items)} due items")
        return items

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
        self.logger.info(f"SRSFilterService: Retrieving cards in learning stage: {stage}")

        if stage == "new":
            # Cards that have never been reviewed
            self.logger.info("SRSFilterService: Querying for new cards (review_count = 0)")
            cards = SRS.query.filter(SRS.review_count == 0).all()
        elif stage == "learning":
            # Cards in initial learning phase (interval <= 1 day but reviewed at least once)
            self.logger.info("SRSFilterService: Querying for learning cards (review_count > 0, interval <= 1.0)")
            cards = SRS.query.filter(SRS.review_count > 0, SRS.interval <= LEARNING_THRESHOLD).all()
        elif stage == "reviewing":
            # Cards in review phase (interval between 1 and 21 days)
            self.logger.info(
                f"SRSFilterService: Querying for reviewing cards (1.0 < interval <= {REVIEWING_THRESHOLD})")
            cards = SRS.query.filter(
                SRS.interval > LEARNING_THRESHOLD,
                SRS.interval <= REVIEWING_THRESHOLD
            ).all()
        elif stage == "mastered":
            # Cards considered mastered (interval > 21 days)
            self.logger.info(f"SRSFilterService: Querying for mastered cards (interval > {REVIEWING_THRESHOLD})")
            cards = SRS.query.filter(SRS.interval > REVIEWING_THRESHOLD).all()
        else:
            self.logger.error(f"SRSFilterService: Unknown learning stage: {stage}")
            raise ValueError(f"Unknown learning stage: {stage}")

        self.logger.info(f"SRSFilterService: Found {len(cards)} cards in {stage} stage")
        return cards

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
        self.logger.info(f"SRSFilterService: Retrieving cards with difficulty: {difficulty}")

        if difficulty == "hard":
            # Hard cards (low ease factor)
            self.logger.info(f"SRSFilterService: Querying for hard cards (ease_factor <= {HARD_THRESHOLD})")
            cards = SRS.query.filter(
                SRS.ease_factor <= HARD_THRESHOLD,
                SRS.review_count > 0
            ).all()  # Only include reviewed cards
        elif difficulty == "medium":
            # Medium difficulty cards
            self.logger.info(
                f"SRSFilterService: Querying for medium cards ({HARD_THRESHOLD} < ease_factor < {MEDIUM_THRESHOLD})")
            cards = SRS.query.filter(
                SRS.ease_factor > HARD_THRESHOLD,
                SRS.ease_factor < MEDIUM_THRESHOLD,
                SRS.review_count > 0
            ).all()
        elif difficulty == "easy":
            # Easy cards (high ease factor)
            self.logger.info(f"SRSFilterService: Querying for easy cards (ease_factor >= {MEDIUM_THRESHOLD})")
            cards = SRS.query.filter(
                SRS.ease_factor >= MEDIUM_THRESHOLD,
                SRS.review_count > 0
            ).all()
        else:
            self.logger.error(f"SRSFilterService: Unknown difficulty: {difficulty}")
            raise ValueError(f"Unknown difficulty: {difficulty}")

        self.logger.info(f"SRSFilterService: Found {len(cards)} cards with {difficulty} difficulty")
        return cards

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
        self.logger.info(f"SRSFilterService: Retrieving cards with user performance: {performance}")

        # Join with review history to calculate statistics
        if performance == "struggling":
            # Cards with low success rate (< 60% correct)
            self.logger.info(
                f"SRSFilterService: Querying for struggling cards (success rate < {STRUGGLING_THRESHOLD}%)")
            cards = SRS.query.filter(
                SRS.review_count > 2,
                (SRS.successful_reps * 100 / SRS.review_count) < STRUGGLING_THRESHOLD
            ).all()  # At least 3 reviews
        elif performance == "average":
            # Cards with average success rate (60-85%)
            self.logger.info(
                f"SRSFilterService: Querying for average performance cards ({STRUGGLING_THRESHOLD}% <= success rate <= {AVERAGE_THRESHOLD}%)")
            cards = SRS.query.filter(
                SRS.review_count > 2,
                (SRS.successful_reps * 100 / SRS.review_count) >= STRUGGLING_THRESHOLD,
                (SRS.successful_reps * 100 / SRS.review_count) <= AVERAGE_THRESHOLD,
            ).all()
        elif performance == "strong":
            # Cards with high success rate (> 85%)
            self.logger.info(
                f"SRSFilterService: Querying for strong performance cards (success rate > {AVERAGE_THRESHOLD}%)")
            cards = SRS.query.filter(
                SRS.review_count > 2,
                (SRS.successful_reps * 100 / SRS.review_count) > AVERAGE_THRESHOLD
            ).all()
        else:
            self.logger.error(f"SRSFilterService: Unknown performance level: {performance}")
            raise ValueError(f"Unknown performance level: {performance}")

        self.logger.info(f"SRSFilterService: Found {len(cards)} cards with {performance} performance")
        return cards

    def get_cards_by_type(self, type_name: str) -> List[SRS]:
        """
        Get all SRS items of a specific type.

        Args:
            type_name: The notable_type to filter by

        Returns:
            List of SRS items of the specified type
        """
        self.logger.info(f"SRSFilterService: Getting all items of type '{type_name}'")
        items = SRS.query.filter(SRS.notable_type == type_name).all()
        self.logger.info(f"SRSFilterService: Found {len(items)} items of type '{type_name}'")
        return items

    def get_review_strategy(self, strategy_name: str, limit: Optional[int] = None) -> List[SRS]:
        """
        Get cards based on various predefined review strategies.

        Args:
            strategy_name: Name of the review strategy ('due_mix', 'priority_first',
                          'hard_cards_first', 'mastery_boost', 'struggling_focus', 'new_mix')
            limit: Optional maximum number of cards to return

        Returns:
            List of cards that match the strategy criteria

        Raises:
            ValueError: If the strategy_name parameter is invalid
        """
        self.logger.info(f"SRSFilterService: Getting cards using review strategy: {strategy_name}, limit: {limit}")
        cards = []

        if strategy_name == "due_mix":
            # A mix of cards from different categories that are due
            self.logger.info("SRSFilterService: Applying 'due_mix' strategy")
            due_cards = self.get_due_items()
            categories = {}

            # Group by category
            for card in due_cards:
                if card.notable_type not in categories:
                    categories[card.notable_type] = []
                categories[card.notable_type].append(card)

            self.logger.info(
                f"SRSFilterService: Found cards in {len(categories)} categories: {list(categories.keys())}")

            # Get a mix of cards from each category
            for category, category_cards in categories.items():
                # Take about 1/3 of cards from each category, but at least 1
                category_limit = max(1, len(category_cards) // 3)
                self.logger.info(f"SRSFilterService: Taking {category_limit} cards from category '{category}'")
                cards.extend(category_cards[:category_limit])

        elif strategy_name == "priority_first":
            # Cards that are most overdue first
            self.logger.info("SRSFilterService: Applying 'priority_first' strategy (most overdue first)")
            cards = (
                SRS.query.filter(
                    SRS.next_review_at.isnot(None),
                    SRS.next_review_at <= datetime.now(ZoneInfo("UTC"))
                )
                .order_by(SRS.next_review_at)
                .all()
            )

        elif strategy_name == "hard_cards_first":
            # Focus on difficult cards first
            self.logger.info("SRSFilterService: Applying 'hard_cards_first' strategy (ease_factor <= 1.7)")
            cards = (
                SRS.query.filter(
                    SRS.next_review_at.isnot(None),
                    SRS.next_review_at <= datetime.now(ZoneInfo("UTC")),
                    SRS.ease_factor <= 1.7
                )
                .order_by(SRS.ease_factor)
                .all()
            )

        elif strategy_name == "mastery_boost":
            # Cards that are close to mastery (interval between 15-21 days)
            self.logger.info("SRSFilterService: Applying 'mastery_boost' strategy (interval between 15-21 days)")
            cards = (
                SRS.query.filter(
                    SRS.next_review_at.isnot(None),
                    SRS.next_review_at <= datetime.now(ZoneInfo("UTC")),
                    SRS.interval >= 15,
                    SRS.interval <= 21,
                )
                .order_by(SRS.interval.desc())
                .all()
            )

        elif strategy_name == "struggling_focus":
            # Focus on cards with low success rate
            self.logger.info("SRSFilterService: Applying 'struggling_focus' strategy (success rate < 70%)")
            cards = (
                SRS.query.filter(
                    SRS.next_review_at.isnot(None),
                    SRS.next_review_at <= datetime.now(ZoneInfo("UTC")),
                    SRS.review_count > 2,
                    (SRS.successful_reps * 100 / SRS.review_count) < 70,
                )
                .order_by((SRS.successful_reps * 100 / SRS.review_count))
                .all()
            )

        elif strategy_name == "new_mix":
            # Mix of new and due cards
            self.logger.info("SRSFilterService: Applying 'new_mix' strategy (mix of new and due cards)")
            new_cards = SRS.query.filter(SRS.review_count == 0).limit(5).all()
            self.logger.info(f"SRSFilterService: Found {len(new_cards)} new cards")

            due_cards = (
                SRS.query.filter(
                    SRS.next_review_at.isnot(None),
                    SRS.next_review_at <= datetime.now(ZoneInfo("UTC")),
                    SRS.review_count > 0
                )
                .limit(10)
                .all()
            )
            self.logger.info(f"SRSFilterService: Found {len(due_cards)} due cards")

            cards = new_cards + due_cards

        else:
            self.logger.error(f"SRSFilterService: Unknown review strategy: {strategy_name}")
            raise ValueError(f"Unknown review strategy: {strategy_name}")

        # Apply limit if specified
        if limit:
            self.logger.info(f"SRSFilterService: Limiting result to {limit} cards")
            cards = cards[:limit]

        self.logger.info(f"SRSFilterService: Strategy '{strategy_name}' returned {len(cards)} cards")
        return cards

    def get_due_cards(self, limit: Optional[int] = None) -> List[SRS]:
        """
        Get SRS items that are due for review.

        Args:
            limit: Optional maximum number of cards to return

        Returns:
            List of SRS items due for review
        """
        self.logger.info(f"SRSFilterService: Getting due cards with limit: {limit}")
        due_items = self.get_due_items()
        self.logger.info(f"SRSFilterService: Found {len(due_items)} due items")

        if limit is not None:
            self.logger.info(f"SRSFilterService: Limiting to {limit} items")
            return due_items[:limit]

        return due_items