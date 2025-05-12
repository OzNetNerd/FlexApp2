"""Analytics service for SRS data metrics and statistics."""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.models.pages.srs import SRS, ReviewHistory
from app.services.srs.constants import (
    DEFAULT_EASE_FACTOR, MASTERY_THRESHOLD,
)
from app.models import db
from app.utils.app_logging import get_logger

logger = get_logger()


class SRSAnalyticsService:
    """Service for SRS metrics, analytics, and statistical calculations."""

    def __init__(self):
        """Initialize the SRS analytics service."""
        self.logger = logger
        self.logger.info("SRSAnalyticsService: Initializing SRS analytics service")

    def count_total(self) -> int:
        """
        Get the total count of SRS items.

        Returns:
            Total number of SRS items
        """
        self.logger.info("SRSAnalyticsService: Counting total SRS items")
        count = SRS.query.count()
        self.logger.info(f"SRSAnalyticsService: Total SRS items: {count}")
        return count

    def count_due_today(self) -> int:
        """
        Get the count of SRS items due for review today.

        Returns:
            Number of SRS items due today
        """
        self.logger.info("SRSAnalyticsService: Counting SRS items due today")
        count = SRS.query.filter(
            SRS.next_review_at.isnot(None),
            SRS.next_review_at <= datetime.now(ZoneInfo("UTC"))
        ).count()

        self.logger.info(f"SRSAnalyticsService: SRS items due today: {count}")
        return count

    def calculate_success_rate(self) -> int:
        """
        Calculate the success rate of SRS items as a percentage.

        Returns:
            Success rate as a percentage (0-100)
        """
        self.logger.info("SRSAnalyticsService: Calculating overall success rate")
        all_items = SRS.query.all()

        if not all_items:
            self.logger.info("SRSAnalyticsService: No items found, success rate is 0")
            return 0

        successful_items = sum(
            1 for item in all_items
            if item.successful_reps and item.review_count and item.review_count > 0
        )

        self.logger.info(
            f"SRSAnalyticsService: Found {successful_items} successful items out of {len(all_items)} total")

        success_rate = int((successful_items / len(all_items)) * 100) if len(all_items) > 0 else 0
        self.logger.info(f"SRSAnalyticsService: Success rate: {success_rate}%")
        return success_rate

    def count_weekly_reviews(self) -> int:
        """
        Count the number of reviews completed in the past 7 days.

        Returns:
            Number of reviews in the past week
        """
        self.logger.info("SRSAnalyticsService: Counting reviews in the past 7 days")
        now = datetime.now(ZoneInfo("UTC"))
        week_ago = now - timedelta(days=7)
        self.logger.info(f"SRSAnalyticsService: Counting reviews between {week_ago.isoformat()} and {now.isoformat()}")

        count = ReviewHistory.query.filter(
            ReviewHistory.created_at >= week_ago,
            ReviewHistory.created_at <= now
        ).count()

        self.logger.info(f"SRSAnalyticsService: Found {count} reviews in the past 7 days")
        return count

    def calculate_retention_increase(self) -> int:
        """
        Calculate the increase in retention rate over the past month compared to the previous month.

        Returns:
            Percentage point increase in retention rate (can be negative)
        """
        self.logger.info("SRSAnalyticsService: Calculating retention rate increase")
        now = datetime.now(ZoneInfo("UTC"))

        # Current month
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.logger.info(f"SRSAnalyticsService: Current month starts at {current_month_start.isoformat()}")

        # Previous month
        if current_month_start.month == 1:
            prev_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
        else:
            prev_month_start = current_month_start.replace(month=current_month_start.month - 1)
        self.logger.info(f"SRSAnalyticsService: Previous month starts at {prev_month_start.isoformat()}")

        # Get reviews for current and previous months
        current_month_reviews = ReviewHistory.query.filter(
            ReviewHistory.created_at >= current_month_start,
            ReviewHistory.created_at < now
        ).all()
        self.logger.info(f"SRSAnalyticsService: Found {len(current_month_reviews)} reviews in current month")

        prev_month_reviews = ReviewHistory.query.filter(
            ReviewHistory.created_at >= prev_month_start,
            ReviewHistory.created_at < current_month_start
        ).all()
        self.logger.info(f"SRSAnalyticsService: Found {len(prev_month_reviews)} reviews in previous month")

        # Calculate success rates
        def calc_success_rate(reviews):
            if not reviews:
                return 0
            successful = sum(1 for r in reviews if r.rating >= 3)
            return (successful / len(reviews)) * 100

        current_rate = calc_success_rate(current_month_reviews)
        previous_rate = calc_success_rate(prev_month_reviews)

        self.logger.info(f"SRSAnalyticsService: Current month success rate: {current_rate:.2f}%")
        self.logger.info(f"SRSAnalyticsService: Previous month success rate: {previous_rate:.2f}%")

        # Calculate increase (percentage points)
        increase = current_rate - previous_rate
        self.logger.info(f"SRSAnalyticsService: Retention rate increase: {increase:.2f} percentage points")

        # Return as integer percentage point increase
        result = int(increase) if previous_rate > 0 else 0
        self.logger.info(f"SRSAnalyticsService: Returning retention increase: {result}%")
        return result

    def count_consecutive_perfect_reviews(self) -> int:
        """
        Count the number of consecutive perfect reviews (rating 4-5) in the most recent history.

        Returns:
            Number of consecutive perfect reviews
        """
        self.logger.info("SRSAnalyticsService: Counting consecutive perfect reviews")
        # Get all review history ordered by time, most recent first
        history = ReviewHistory.query.order_by(ReviewHistory.created_at.desc()).all()
        self.logger.info(f"SRSAnalyticsService: Found {len(history)} total reviews in history")

        # Count consecutive perfect reviews
        consecutive_count = 0
        for review in history:
            if review.rating >= 4:  # Ratings 4-5 are considered "perfect"
                consecutive_count += 1
                self.logger.info(f"SRSAnalyticsService: Review {review.id} was perfect (rating {review.rating})")
            else:
                # Stop counting as soon as we hit a non-perfect review
                self.logger.info(
                    f"SRSAnalyticsService: Found non-perfect review {review.id} (rating {review.rating}), stopping count")
                break

        self.logger.info(f"SRSAnalyticsService: Total consecutive perfect reviews: {consecutive_count}")
        return consecutive_count

    def get_learning_progress_data(self, months: int = 7) -> Dict[str, Any]:
        """
        Get historical learning progress data for charts.

        Args:
            months: Number of past months to include in the data

        Returns:
            Dictionary with labels and datasets for charting
        """
        self.logger.info(f"SRSAnalyticsService: Getting learning progress data for past {months} months")
        # Create month labels based on current month
        now = datetime.now(ZoneInfo("UTC"))
        labels = []

        for i in range(months):
            # Calculate month by going backward from current month
            month_date = now.replace(day=1) - timedelta(days=30 * i)
            month_name = month_date.strftime("%b")
            labels.insert(0, month_name)  # Insert at beginning to get chronological order
            self.logger.info(f"SRSAnalyticsService: Added month label: {month_name}")

        # For now, use sample data similar to what's in the dashboard route
        # In a production environment, this would be calculated from actual database records

        # Sample data (these would ideally be calculated from ReviewHistory)
        mastered = [5, 9, 12, 18, 22, 28, 35][:months]
        added = [8, 12, 15, 20, 25, 30, 47][:months]
        retention = [60, 65, 70, 72, 75, 80, 83][:months]

        self.logger.info(f"SRSAnalyticsService: Sample data - Mastered: {mastered}")
        self.logger.info(f"SRSAnalyticsService: Sample data - Added: {added}")
        self.logger.info(f"SRSAnalyticsService: Sample data - Retention: {retention}")

        # Create datasets
        datasets = [
            {"label": "Cards Mastered", "data": mastered},
            {"label": "Cards Added", "data": added},
            {"label": "Retention Score", "data": retention},
        ]

        result = {"labels": labels, "datasets": datasets}
        self.logger.info("SRSAnalyticsService: Returning learning progress data")
        return result

    def count_mastered_cards_this_month(self) -> int:
        """
        Count the number of cards that became mastered this month.

        Returns:
            Number of cards that crossed the mastery threshold this month
        """
        self.logger.info("SRSAnalyticsService: Counting cards mastered this month")
        # Define mastery threshold
        mastery_threshold = MASTERY_THRESHOLD  # 30 days interval as mastery threshold
        self.logger.info(f"SRSAnalyticsService: Using mastery threshold of {mastery_threshold} days")

        # Get current month range
        now = datetime.now(ZoneInfo("UTC"))
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.logger.info(f"SRSAnalyticsService: Calculating for current month starting {first_of_month.isoformat()}")

        # Find cards that have reached mastery this month
        # We can determine this by looking at review history entries where the interval
        # crossed the mastery threshold during this month
        mastered_cards = 0

        # Get unique cards with reviews this month
        month_reviews = ReviewHistory.query.filter(ReviewHistory.created_at >= first_of_month).all()
        self.logger.info(f"SRSAnalyticsService: Found {len(month_reviews)} reviews this month")

        # Get unique card IDs with intervals crossing the threshold this month
        mastered_card_ids = set()
        for review in month_reviews:
            if review.interval >= mastery_threshold:
                self.logger.info(
                    f"SRSAnalyticsService: Found review with interval {review.interval} for item {review.srs_item_id}")
                # Check if this is the first time the card crossed the threshold
                prev_reviews = (
                    ReviewHistory.query.filter(
                        ReviewHistory.srs_item_id == review.srs_item_id,
                        ReviewHistory.timestamp < review.timestamp
                    )
                    .order_by(ReviewHistory.timestamp.desc())
                    .first()
                )

                # If no previous reviews or previous review had interval < threshold
                if not prev_reviews or prev_reviews.interval < mastery_threshold:
                    self.logger.info(f"SRSAnalyticsService: Item {review.srs_item_id} became mastered this month")
                    mastered_card_ids.add(review.srs_item_id)

        result = len(mastered_card_ids)
        self.logger.info(f"SRSAnalyticsService: Total cards mastered this month: {result}")
        return result

    def get_stats(self) -> Dict[str, int]:
        """
        Get current SRS system statistics.

        Returns:
            Dictionary with basic statistics
        """
        self.logger.info("SRSAnalyticsService: Getting system statistics")
        total = SRS.query.count()
        self.logger.info(f"SRSAnalyticsService: Total cards: {total}")

        due_today = SRS.query.filter(SRS.next_review_at <= datetime.now(ZoneInfo("UTC"))).count()
        self.logger.info(f"SRSAnalyticsService: Cards due today: {due_today}")

        today_start = datetime.now(ZoneInfo("UTC")).replace(hour=0, minute=0, second=0, microsecond=0)
        reviewed_today = ReviewHistory.query.filter(ReviewHistory.created_at >= today_start).count()
        self.logger.info(f"SRSAnalyticsService: Cards reviewed today: {reviewed_today}")

        stats = {
            "total_cards": total,
            "cards_due": due_today,
            "cards_reviewed_today": reviewed_today
        }

        self.logger.info(f"SRSAnalyticsService: Returning statistics: {stats}")
        return stats

    def get_detailed_stats(self) -> Dict[str, Any]:
        """
        Get detailed learning statistics for analysis.

        Returns:
            Dictionary with comprehensive statistics about the SRS system
        """
        self.logger.info("SRSAnalyticsService: Getting detailed statistics")
        basic_stats = self.get_stats()
        self.logger.info(f"SRSAnalyticsService: Basic stats: {basic_stats}")

        all_cards = SRS.query.all()
        self.logger.info(f"SRSAnalyticsService: Found {len(all_cards)} total cards")

        self.logger.info("SRSAnalyticsService: Calculating learning stage counts")
        learning_stages = self.get_learning_stages_counts()
        self.logger.info(f"SRSAnalyticsService: Learning stages: {learning_stages}")

        self.logger.info("SRSAnalyticsService: Calculating difficulty counts")
        difficulty_counts = self.get_difficulty_counts()
        self.logger.info(f"SRSAnalyticsService: Difficulty counts: {difficulty_counts}")

        self.logger.info("SRSAnalyticsService: Calculating performance counts")
        performance_counts = self.get_performance_counts()
        self.logger.info(f"SRSAnalyticsService: Performance counts: {performance_counts}")

        self.logger.info("SRSAnalyticsService: Calculating average values")
        avg_ease = sum(card.ease_factor or DEFAULT_EASE_FACTOR for card in all_cards) / len(
            all_cards) if all_cards else DEFAULT_EASE_FACTOR
        avg_interval = sum(card.interval or 0 for card in all_cards) / len(all_cards) if all_cards else 0
        self.logger.info(
            f"SRSAnalyticsService: Average ease factor: {avg_ease:.2f}, average interval: {avg_interval:.2f}")

        streak_days = self.get_streak_days()
        weekly_reviews = self.count_weekly_reviews()
        mastered_this_month = self.count_mastered_cards_this_month()

        self.logger.info(
            f"SRSAnalyticsService: Streak days: {streak_days}, weekly reviews: {weekly_reviews}, mastered this month: {mastered_this_month}")

        stats = {
            **basic_stats,
            "average_ease_factor": avg_ease,
            "average_interval": avg_interval,
            "learning_stages": learning_stages,
            "difficulty_counts": difficulty_counts,
            "performance_counts": performance_counts,
            "streak_days": streak_days,
            "weekly_reviews": weekly_reviews,
            "mastered_this_month": mastered_this_month,
        }

        self.logger.info("SRSAnalyticsService: Returning detailed statistics")
        return stats

    def count_reviews_today(self) -> int:
        """
        Count the number of reviews completed today.

        Returns:
            Number of reviews completed today
        """
        self.logger.info("SRSAnalyticsService: Counting reviews completed today")
        today_start = datetime.now(ZoneInfo("UTC")).replace(hour=0, minute=0, second=0, microsecond=0)
        self.logger.info(f"SRSAnalyticsService: Today started at {today_start.isoformat()}")

        count = ReviewHistory.query.filter(ReviewHistory.created_at >= today_start).count()
        self.logger.info(f"SRSAnalyticsService: Found {count} reviews completed today")
        return count

    def get_learning_stages_counts(self) -> Dict[str, int]:
        """
        Get counts of cards by learning stage.

        Returns:
            Dictionary with counts for each learning stage
        """
        self.logger.info("SRSAnalyticsService: Getting counts by learning stage")

        # New cards (never reviewed)
        new_count = SRS.query.filter(SRS.review_count == 0).count()

        # Learning cards (interval <= 1 day but reviewed at least once)
        learning_count = SRS.query.filter(SRS.review_count > 0, SRS.interval <= 1.0).count()

        # Reviewing cards (interval between 1 and 21 days)
        reviewing_count = SRS.query.filter(SRS.interval > 1.0, SRS.interval <= 21.0).count()

        # Mastered cards (interval > 21 days)
        mastered_count = SRS.query.filter(SRS.interval > 21.0).count()

        counts = {
            "new": new_count,
            "learning": learning_count,
            "reviewing": reviewing_count,
            "mastered": mastered_count,
        }

        self.logger.info(f"SRSAnalyticsService: Learning stage counts: {counts}")
        return counts

    def get_difficulty_counts(self) -> Dict[str, int]:
        """
        Get counts of cards by difficulty level.

        Returns:
            Dictionary with counts for each difficulty level
        """
        self.logger.info("SRSAnalyticsService: Getting counts by difficulty level")

        # Hard cards (low ease factor)
        hard_count = SRS.query.filter(SRS.ease_factor <= 1.5, SRS.review_count > 0).count()

        # Medium difficulty cards
        medium_count = SRS.query.filter(
            SRS.ease_factor > 1.5,
            SRS.ease_factor < 2.0,
            SRS.review_count > 0
        ).count()

        # Easy cards (high ease factor)
        easy_count = SRS.query.filter(
            SRS.ease_factor >= 2.0,
            SRS.review_count > 0
        ).count()

        counts = {
            "hard": hard_count,
            "medium": medium_count,
            "easy": easy_count,
        }

        self.logger.info(f"SRSAnalyticsService: Difficulty counts: {counts}")
        return counts

    def get_performance_counts(self) -> Dict[str, int]:
        """
        Get counts of cards by performance level.

        Returns:
            Dictionary with counts for each performance level
        """
        self.logger.info("SRSAnalyticsService: Getting counts by performance level")

        # Cards with low success rate (< 60% correct)
        struggling_count = SRS.query.filter(
            SRS.review_count > 2,
            (SRS.successful_reps * 100 / SRS.review_count) < 60
        ).count()

        # Cards with average success rate (60-85%)
        average_count = SRS.query.filter(
            SRS.review_count > 2,
            (SRS.successful_reps * 100 / SRS.review_count) >= 60,
            (SRS.successful_reps * 100 / SRS.review_count) <= 85,
        ).count()

        # Cards with high success rate (> 85%)
        strong_count = SRS.query.filter(
            SRS.review_count > 2,
            (SRS.successful_reps * 100 / SRS.review_count) > 85
        ).count()

        counts = {
            "struggling": struggling_count,
            "average": average_count,
            "strong": strong_count,
        }

        self.logger.info(f"SRSAnalyticsService: Performance counts: {counts}")
        return counts

    def get_streak_days(self) -> int:
        """
        Calculate the current streak of consecutive days with SRS reviews.

        Returns:
            Number of consecutive days with at least one review
        """
        self.logger.info("SRSAnalyticsService: Calculating review streak days")
        # Get dates with activity
        today = datetime.now(ZoneInfo("UTC")).date()
        history_dates = set(h.created_at.date() for h in ReviewHistory.query.all())
        self.logger.info(f"SRSAnalyticsService: Found activity on {len(history_dates)} different days")

        if not history_dates:
            self.logger.info("SRSAnalyticsService: No review history, streak is 0")
            return 0

        # Calculate streak
        streak = 0
        current_date = today

        # Check if there was activity today
        if today in history_dates:
            self.logger.info("SRSAnalyticsService: Found activity today")
            streak = 1
            current_date = today - timedelta(days=1)
        else:
            # If no activity today, check yesterday
            yesterday = today - timedelta(days=1)
            if yesterday in history_dates:
                self.logger.info("SRSAnalyticsService: Found activity yesterday")
                streak = 1
                current_date = yesterday - timedelta(days=1)
            else:
                self.logger.info("SRSAnalyticsService: No recent activity, streak is 0")
                return 0  # No streak

        # Check previous days
        days_checked = 0
        while current_date in history_dates and days_checked < 365:  # Prevent infinite loop with 1-year limit
            streak += 1
            self.logger.info(f"SRSAnalyticsService: Found activity on {current_date}, streak now {streak}")
            current_date = current_date - timedelta(days=1)
            days_checked += 1

        self.logger.info(f"SRSAnalyticsService: Final streak count: {streak} days")
        return streak

    def calculate_progress_by_type(self, type_name: Optional[str] = None) -> Union[int, Dict[str, int]]:
        """
        Calculate the learning progress for cards of a specific type.

        Progress is calculated as the percentage of successful repetitions out of total reviews.

        Args:
            type_name: Optional notable_type to filter by

        Returns:
            Progress percentage (0-100) if type_name provided, or dictionary mapping types to progress
        """
        if type_name:
            self.logger.info(f"SRSAnalyticsService: Calculating progress for type: {type_name}")
        else:
            self.logger.info("SRSAnalyticsService: Calculating progress for all types")

        all_items = SRS.query.all()

        def calculate_progress(cards):
            if not cards:
                return 0
            total_progress = sum(
                (item.successful_reps or 0) / max(item.review_count or 1, 1) * 100
                for item in cards
            )
            return int(total_progress / len(cards)) if cards else 0

        if type_name:
            # Filter items by type
            type_items = [item for item in all_items if item.notable_type == type_name]
            self.logger.info(f"SRSAnalyticsService: Found {len(type_items)} items of type '{type_name}'")
            progress = calculate_progress(type_items)
            self.logger.info(f"SRSAnalyticsService: Progress for type '{type_name}': {progress}%")
            return progress
        else:
            # Calculate progress for each type
            company_items = [item for item in all_items if item.notable_type == "company"]
            contact_items = [item for item in all_items if item.notable_type == "contact"]
            opportunity_items = [item for item in all_items if item.notable_type == "opportunity"]

            self.logger.info(
                f"SRSAnalyticsService: Found {len(company_items)} company items, "
                f"{len(contact_items)} contact items, {len(opportunity_items)} opportunity items"
            )

            progress = {
                "company": calculate_progress(company_items),
                "contact": calculate_progress(contact_items),
                "opportunity": calculate_progress(opportunity_items),
                "overall": calculate_progress(all_items),
            }

            self.logger.info(f"SRSAnalyticsService: Progress by type: {progress}")
            return progress

    def count_due_by_type(self, type_name: Optional[str] = None) -> Union[int, Dict[str, int]]:
        """
        Count SRS items that are due for review, grouped by notable_type.

        Args:
            type_name: Optional notable_type to filter by

        Returns:
            Count if type_name provided, or dictionary mapping types to counts
        """
        # Get all due items
        self.logger.info("SRSAnalyticsService: Counting due items by type")
        due_items = SRS.query.filter(
            SRS.next_review_at.isnot(None),
            SRS.next_review_at <= datetime.now(ZoneInfo("UTC"))
        ).all()

        self.logger.info(f"SRSAnalyticsService: Found {len(due_items)} total due items")

        if type_name:
            self.logger.info(f"SRSAnalyticsService: Counting due items for specific type: {type_name}")
            # Count due items of the specific type
            count = sum(1 for item in due_items if item.notable_type == type_name)
            self.logger.info(f"SRSAnalyticsService: Found {count} due items of type '{type_name}'")
            return count
        else:
            # Initialize counts dictionary
            counts = {"company": 0, "contact": 0, "opportunity": 0, "other": 0}  # For any items with unrecognized types

            # Count due items by type
            for item in due_items:
                item_type = item.notable_type
                if item_type in counts:
                    counts[item_type] += 1
                else:
                    counts["other"] += 1

            self.logger.info(f"SRSAnalyticsService: Due items by type: {counts}")
            return counts

    def count_by_type(self, type_name: Optional[str] = None) -> Union[int, Dict[str, int]]:
        """
        Count SRS items grouped by notable_type.

        Args:
            type_name: Optional notable_type to filter by

        Returns:
            Count if type_name provided, or dictionary mapping types to counts
        """
        self.logger.info("SRSAnalyticsService: Counting all items by type")

        if type_name:
            self.logger.info(f"SRSAnalyticsService: Counting items for specific type: {type_name}")
            # Count items of the specific type
            count = SRS.query.filter(SRS.notable_type == type_name).count()
            self.logger.info(f"SRSAnalyticsService: Found {count} items of type '{type_name}'")
            return count
        else:
            # Get distinct types and counts using SQLAlchemy
            counts = {"company": 0, "contact": 0, "opportunity": 0, "other": 0}

            # Get counts for known types
            for type_name in ["company", "contact", "opportunity"]:
                counts[type_name] = SRS.query.filter(SRS.notable_type == type_name).count()

            # Count any other types
            other_count = SRS.query.filter(
                ~SRS.notable_type.in_(["company", "contact", "opportunity"])
            ).count()
            counts["other"] = other_count

            self.logger.info(f"SRSAnalyticsService: Items by type: {counts}")
            return counts