from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from zoneinfo import ZoneInfo
from app.models.pages.srs import SRS, ReviewHistory
from app.utils.app_logging import get_logger
from app.models import db

logger = get_logger()

# Constants for interval calculations (copied from your pasted code)
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


# Import the service class from your pasted code
class SRSService:
    """Service for managing SRS items and scheduling reviews based on spaced repetition principles."""

    # Map UI ratings 0-5 to FSRS/SM2 ratings 1-4
    UI_TO_FSRS_RATING = {0: 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4}

    def __init__(self):
        """Initialize the SRS service."""
        logger.info("SRSService: Initializing SRS service")
        pass

    def get_by_id(self, item_id: int) -> SRS:
        """Get an SRS item by ID."""
        logger.info(f"SRSService: Retrieving SRS item with ID {item_id}")
        item = SRS.query.get(item_id)
        if item:
            logger.info(f"SRSService: Successfully retrieved SRS item {item_id}")
        else:
            logger.info(f"SRSService: SRS item with ID {item_id} not found")
        return item

    def get_all(self) -> list:
        """Get all SRS items."""
        logger.info("SRSService: Retrieving all SRS items")
        items = SRS.query.all()
        logger.info(f"SRSService: Retrieved {len(items)} SRS items")
        return items

    def update(self, item_id_or_obj, update_data):
        """Update an SRS item."""
        if isinstance(item_id_or_obj, int):
            item = self.get_by_id(item_id_or_obj)
            if not item:
                raise ValueError(f"SRS item with ID {item_id_or_obj} not found")
        else:
            item = item_id_or_obj

        for key, value in update_data.items():
            setattr(item, key, value)
        item.save()
        return item

    def preview_ratings(self, item_id: int) -> dict:
        """Preview the next intervals for each possible rating of an item."""
        logger.info(f"SRSService: Previewing intervals for all ratings for item {item_id}")
        item = self.get_by_id(item_id)
        if not item:
            logger.error(f"SRSService: SRS item with ID {item_id} not found during preview_ratings")
            raise ValueError(f"SRS item with ID {item_id} not found")

        results = {}
        for ui_rating in range(6):  # UI Ratings 0-5
            next_interval = self._calculate_next_interval(item, ui_rating)
            results[ui_rating] = round(next_interval, 1)

        logger.info(f"SRSService: Interval previews for item {item_id}: {results}")
        return results

    def schedule_review(self, item_id: int, rating: int, answer_given="") -> SRS:
        """Schedule the next review for an item based on the user's rating."""
        logger.info(f"SRSService: Scheduling review for item {item_id} with rating {rating}")
        item = self.get_by_id(item_id)
        if not item:
            logger.error(f"SRSService: SRS item with ID {item_id} not found during schedule_review")
            raise ValueError(f"SRS item with ID {item_id} not found")

        # Set default ease factor for new cards
        if item.review_count == 0 and (item.ease_factor is None or item.ease_factor == 0):
            logger.info(f"SRSService: Setting default ease factor for new item {item_id}")
            item.ease_factor = DEFAULT_EASE_FACTOR

        # Calculate next interval and ease factor
        next_interval = self._calculate_next_interval(item, rating)
        new_ease = self._calculate_new_ease_factor(item, rating)
        logger.info(f"SRSService: Calculated next interval: {next_interval:.2f} days, new ease factor: {new_ease:.2f}")

        # Calculate next review date - Fixed timezone issue
        next_review_at = datetime.now(ZoneInfo("UTC")) + timedelta(days=next_interval)
        logger.info(f"SRSService: Next review scheduled for {next_review_at.isoformat()}")

        # Track successful repetitions (ratings ≥ 3)
        successful_reps = item.successful_reps or 0
        if rating >= 3:
            successful_reps += 1
            logger.info(f"SRSService: Incrementing successful repetitions to {successful_reps}")

        # Update item properties
        update_data = {
            "ease_factor": new_ease,
            "interval": next_interval,
            "successful_reps": successful_reps,
            "review_count": (item.review_count or 0) + 1,
            "next_review_at": next_review_at,
            "last_rating": rating,
            "last_reviewed_at": datetime.now(ZoneInfo("UTC")),
        }

        # Persist updated SRS
        logger.info(f"SRSService: updating item {item.id} → next in {next_interval:.2f}d, ef={new_ease:.2f}")
        self.update(item, update_data)

        # Record history
        logger.info(f"SRSService: Creating review history record for item {item.id}")
        history = ReviewHistory(
            srs_item_id=item.id,
            rating=rating,
            interval=next_interval,
            ease_factor=new_ease,
        )
        history.save()
        logger.info(f"SRSService: logged review {history.id} for item {item.id}")

        if answer_given:
            logger.info(f"SRSService: Handling answer provided for item {item.id}")
            # Add to history or separate table as needed
            pass

        return item

    def get_filtered_cards(self, filters=None):
        """Get SRS cards filtered by various criteria."""
        logger.info(f"SRSService: Getting filtered cards with filters: {filters}")
        # Start with base query
        query = SRS.query

        # Apply filters if provided
        if filters:
            # Due cards filter
            if filters.get("due_only"):
                logger.info("SRSService: Applying due_only filter")
                # Add a condition to filter out NULL next_review_at values
                query = query.filter(SRS.next_review_at.isnot(None), SRS.next_review_at <= datetime.now(ZoneInfo("UTC")))

            # Category filter
            if filters.get("category"):
                logger.info(f"SRSService: Applying category filter: {filters['category']}")
                query = query.filter(SRS.notable_type == filters["category"])

            # Text search in question or answer
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                logger.info(f"SRSService: Applying search filter: {filters['search']}")
                query = query.filter((SRS.question.ilike(search_term)) | (SRS.answer.ilike(search_term)))

            # Interval range
            if filters.get("min_interval") is not None:
                logger.info(f"SRSService: Applying min_interval filter: {filters['min_interval']}")
                query = query.filter(SRS.interval >= filters["min_interval"])
            if filters.get("max_interval") is not None:
                logger.info(f"SRSService: Applying max_interval filter: {filters['max_interval']}")
                query = query.filter(SRS.interval <= filters["max_interval"])

            # Ease factor range
            if filters.get("min_ease") is not None:
                logger.info(f"SRSService: Applying min_ease filter: {filters['min_ease']}")
                query = query.filter(SRS.ease_factor >= filters["min_ease"])
            if filters.get("max_ease") is not None:
                logger.info(f"SRSService: Applying max_ease filter: {filters['max_ease']}")
                query = query.filter(SRS.ease_factor <= filters["max_ease"])

            # Sort order
            sort_field = getattr(SRS, filters.get("sort_by", "next_review_at"))
            if filters.get("sort_order") == "desc":
                logger.info(f"SRSService: Applying descending sort on {filters.get('sort_by', 'next_review_at')}")
                sort_field = sort_field.desc()
            query = query.order_by(sort_field)

        # Execute query
        result = query.all()
        logger.info(f"SRSService: Filtered query returned {len(result)} cards")
        return result

    def count_total(self):
        """Get the total count of SRS items."""
        logger.info("SRSService: Counting total SRS items")
        count = SRS.query.count()
        logger.info(f"SRSService: Total SRS items: {count}")
        return count

    def count_due_today(self):
        """Get the count of SRS items due for review today."""
        logger.info("SRSService: Counting SRS items due today")
        count = SRS.query.filter(SRS.next_review_at.isnot(None), SRS.next_review_at <= datetime.now(ZoneInfo("UTC"))).count()
        logger.info(f"SRSService: SRS items due today: {count}")
        return count

    def calculate_success_rate(self):
        """Calculate the success rate of SRS items as a percentage."""
        logger.info("SRSService: Calculating overall success rate")
        all_items = self.get_all()
        if not all_items:
            logger.info("SRSService: No items found, success rate is 0")
            return 0

        successful_items = sum(1 for item in all_items if item.successful_reps and item.review_count and item.review_count > 0)
        logger.info(f"SRSService: Found {successful_items} successful items out of {len(all_items)} total")

        success_rate = int((successful_items / len(all_items)) * 100) if len(all_items) > 0 else 0
        logger.info(f"SRSService: Success rate: {success_rate}%")
        return success_rate

    def get_due_items(self) -> list:
        """Get all SRS items that are due for review."""
        logger.info("SRSService: Retrieving all due SRS items")
        items = SRS.query.filter(SRS.next_review_at.isnot(None), SRS.next_review_at <= datetime.now(ZoneInfo("UTC"))).all()
        logger.info(f"SRSService: Found {len(items)} due items")
        return items

    def _calculate_next_interval(self, item: SRS, ui_rating: int) -> float:
        """Calculate the next interval based on the rating and current item state."""
        logger.info(f"SRSService: Calculating next interval for item {item.id} with UI rating {ui_rating}")
        fsrs_rating = self.UI_TO_FSRS_RATING.get(ui_rating, 1)  # Default to 1 if invalid
        logger.info(f"SRSService: Mapped UI rating {ui_rating} to FSRS rating {fsrs_rating}")

        # Fix: use review_count instead of repetition
        if item.review_count == 0 or item.interval <= 0:
            logger.info(f"SRSService: Item {item.id} is new or has invalid interval, applying initial learning steps")
            # Use graduated learning steps (10min → 1h → 6h → 1d)
            if fsrs_rating == 1:
                interval = MIN_INTERVAL  # 10 minutes
                logger.info(f"SRSService: Rating 1 (Again) - setting interval to {interval:.4f} days (10 min)")
                return interval
            elif fsrs_rating == 2:
                interval = SHORT_INTERVAL  # 1 hour
                logger.info(f"SRSService: Rating 2 (Hard) - setting interval to {interval:.4f} days (1 hour)")
                return interval
            elif fsrs_rating == 3:
                interval = MEDIUM_INTERVAL  # 6 hours
                logger.info(f"SRSService: Rating 3 (Good) - setting interval to {interval:.4f} days (6 hours)")
                return interval
            else:
                interval = GOOD_INITIAL_INTERVAL  # 3 days
                logger.info(f"SRSService: Rating 4 (Easy) - setting interval to {interval:.1f} days")
                return interval
        else:
            logger.info(f"SRSService: Item {item.id} is in review phase, applying spacing effect")
            # Apply spacing effect for reviews
            if fsrs_rating == 1:
                interval = SHORT_INTERVAL  # Reset to 1 hour for failed reviews
                logger.info(f"SRSService: Rating 1 (Again) - resetting interval to {interval:.4f} days (1 hour)")
                return interval
            elif fsrs_rating == 2:
                interval = min(item.interval * HARD_MULTIPLIER, MAX_INTERVAL)
                logger.info(f"SRSService: Rating 2 (Hard) - setting interval to {interval:.2f} days (x{HARD_MULTIPLIER})")
                return interval
            elif fsrs_rating == 3:
                interval = min(item.interval * GOOD_MULTIPLIER, MAX_INTERVAL)
                logger.info(f"SRSService: Rating 3 (Good) - setting interval to {interval:.2f} days (x{GOOD_MULTIPLIER})")
                return interval
            else:
                interval = min(item.interval * EASY_MULTIPLIER, MAX_INTERVAL)
                logger.info(f"SRSService: Rating 4 (Easy) - setting interval to {interval:.2f} days (x{EASY_MULTIPLIER})")
                return interval

    def _calculate_new_ease_factor(self, item: SRS, ui_rating: int) -> float:
        """Calculate the new ease factor based on the rating."""
        logger.info(f"SRSService: Calculating new ease factor for item {item.id} with UI rating {ui_rating}")
        fsrs_rating = self.UI_TO_FSRS_RATING.get(ui_rating, 1)  # Default to 1 if invalid
        current_ease = item.ease_factor or DEFAULT_EASE_FACTOR
        logger.info(f"SRSService: Current ease factor: {current_ease:.2f}")

        if fsrs_rating == 1:
            new_ease = max(MIN_EASE_FACTOR, current_ease - FAIL_EASE_PENALTY)
            logger.info(f"SRSService: Rating 1 (Again) - reducing ease by {FAIL_EASE_PENALTY} to {new_ease:.2f}")
            return new_ease
        elif fsrs_rating == 2:
            new_ease = max(MIN_EASE_FACTOR, current_ease - HARD_EASE_PENALTY)
            logger.info(f"SRSService: Rating 2 (Hard) - reducing ease by {HARD_EASE_PENALTY} to {new_ease:.2f}")
            return new_ease
        elif fsrs_rating == 3:
            logger.info(f"SRSService: Rating 3 (Good) - keeping ease at {current_ease:.2f}")
            return current_ease  # No change
        else:
            new_ease = min(MAX_EASE_FACTOR, current_ease + EASY_EASE_BONUS)
            logger.info(f"SRSService: Rating 4 (Easy) - increasing ease by {EASY_EASE_BONUS} to {new_ease:.2f}")
            return new_ease

    def get_next_due_item_id(self, current_item_id=None):
        """Get the next item due for review after current_item_id."""
        logger.info(f"SRSService: Finding next due item after item ID {current_item_id}")
        query = SRS.query.filter(SRS.next_review_at.isnot(None), SRS.next_review_at <= datetime.now(ZoneInfo("UTC")))

        if current_item_id:
            # Try to find the next item in sequence
            logger.info(f"SRSService: Searching for items with ID > {current_item_id}")
            next_items = query.filter(SRS.id > current_item_id).order_by(SRS.id).limit(1).all()
            if next_items:
                logger.info(f"SRSService: Found next due item: {next_items[0].id}")
                return next_items[0].id

        # Otherwise get the first due item
        logger.info("SRSService: No next item found, retrieving first due item")
        first_item = query.order_by(SRS.next_review_at).first()
        result_id = first_item.id if first_item else current_item_id
        logger.info(f"SRSService: Returning item ID: {result_id}")
        return result_id

    def get_prev_item_id(self, current_item_id):
        """Get the previous item reviewed before current_item_id."""
        logger.info(f"SRSService: Finding previous item before item ID {current_item_id}")
        prev_items = SRS.query.filter(SRS.id < current_item_id).order_by(SRS.id.desc()).limit(1).all()
        result_id = prev_items[0].id if prev_items else current_item_id
        logger.info(f"SRSService: Returning previous item ID: {result_id}")
        return result_id

    def get_item_position(self, item_id):
        """Get the position of the item in the current review queue."""
        logger.info(f"SRSService: Calculating position of item {item_id} in review queue")
        item = self.get_by_id(item_id)
        if not item:
            logger.info(f"SRSService: Item {item_id} not found, returning position 1")
            return 1

        # Count items before this one
        position = SRS.query.filter(SRS.next_review_at <= item.next_review_at, SRS.id <= item_id).count()
        logger.info(f"SRSService: Item {item_id} is at position {position} in review queue")

        return position

    def get_streak_days(self):
        """Calculate the current streak of consecutive days with SRS reviews."""
        logger.info("SRSService: Calculating review streak days")
        # Get dates with activity
        today = datetime.now(ZoneInfo("UTC")).date()
        history_dates = set(h.created_at.date() for h in ReviewHistory.query.all())
        logger.info(f"SRSService: Found activity on {len(history_dates)} different days")

        if not history_dates:
            logger.info("SRSService: No review history, streak is 0")
            return 0

        # Calculate streak
        streak = 0
        current_date = today

        # Check if there was activity today
        if today in history_dates:
            logger.info("SRSService: Found activity today")
            streak = 1
            current_date = today - timedelta(days=1)
        else:
            # If no activity today, check yesterday
            yesterday = today - timedelta(days=1)
            if yesterday in history_dates:
                logger.info("SRSService: Found activity yesterday")
                streak = 1
                current_date = yesterday - timedelta(days=1)
            else:
                logger.info("SRSService: No recent activity, streak is 0")
                return 0  # No streak

        # Check previous days
        days_checked = 0
        while current_date in history_dates and days_checked < 365:  # Prevent infinite loop with 1-year limit
            streak += 1
            logger.info(f"SRSService: Found activity on {current_date}, streak now {streak}")
            current_date = current_date - timedelta(days=1)
            days_checked += 1

        logger.info(f"SRSService: Final streak count: {streak} days")
        return streak

    def count_mastered_cards_this_month(self):
        """Count the number of cards that became mastered this month."""
        logger.info("SRSService: Counting cards mastered this month")
        # Define mastery threshold
        mastery_threshold = 30  # 30 days interval as mastery threshold
        logger.info(f"SRSService: Using mastery threshold of {mastery_threshold} days")

        # Get current month range
        now = datetime.now(ZoneInfo("UTC"))
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        logger.info(f"SRSService: Calculating for current month starting {first_of_month.isoformat()}")

        # Find cards that have reached mastery this month
        # We can determine this by looking at review history entries where the interval
        # crossed the mastery threshold during this month
        mastered_cards = 0

        # Get unique cards with reviews this month
        month_reviews = ReviewHistory.query.filter(ReviewHistory.created_at >= first_of_month).all()
        logger.info(f"SRSService: Found {len(month_reviews)} reviews this month")

        # Get unique card IDs with intervals crossing the threshold this month
        mastered_card_ids = set()
        for review in month_reviews:
            if review.interval >= mastery_threshold:
                logger.info(f"SRSService: Found review with interval {review.interval} for item {review.srs_item_id}")
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
                    logger.info(f"SRSService: Item {review.srs_item_id} became mastered this month")
                    mastered_card_ids.add(review.srs_item_id)

        result = len(mastered_card_ids)
        logger.info(f"SRSService: Total cards mastered this month: {result}")
        return result

    def count_weekly_reviews(self):
        """Count the number of reviews completed in the past 7 days."""
        logger.info("SRSService: Counting reviews in the past 7 days")
        now = datetime.now(ZoneInfo("UTC"))
        week_ago = now - timedelta(days=7)
        logger.info(f"SRSService: Counting reviews between {week_ago.isoformat()} and {now.isoformat()}")

        count = ReviewHistory.query.filter(ReviewHistory.created_at >= week_ago, ReviewHistory.created_at <= now).count()
        logger.info(f"SRSService: Found {count} reviews in the past 7 days")
        return count

    def calculate_retention_increase(self):
        """Calculate the increase in retention rate over the past month compared to the previous month."""
        logger.info("SRSService: Calculating retention rate increase")
        now = datetime.now(ZoneInfo("UTC"))

        # Current month
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        logger.info(f"SRSService: Current month starts at {current_month_start.isoformat()}")

        # Previous month
        if current_month_start.month == 1:
            prev_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
        else:
            prev_month_start = current_month_start.replace(month=current_month_start.month - 1)
        logger.info(f"SRSService: Previous month starts at {prev_month_start.isoformat()}")

        # Get reviews for current and previous months
        current_month_reviews = ReviewHistory.query.filter(
            ReviewHistory.created_at >= current_month_start, ReviewHistory.created_at < now
        ).all()
        logger.info(f"SRSService: Found {len(current_month_reviews)} reviews in current month")

        prev_month_reviews = ReviewHistory.query.filter(
            ReviewHistory.created_at >= prev_month_start, ReviewHistory.created_at < current_month_start
        ).all()
        logger.info(f"SRSService: Found {len(prev_month_reviews)} reviews in previous month")

        # Calculate success rates
        def calc_success_rate(reviews):
            if not reviews:
                return 0
            successful = sum(1 for r in reviews if r.rating >= 3)
            return (successful / len(reviews)) * 100

        current_rate = calc_success_rate(current_month_reviews)
        previous_rate = calc_success_rate(prev_month_reviews)

        logger.info(f"SRSService: Current month success rate: {current_rate:.2f}%")
        logger.info(f"SRSService: Previous month success rate: {previous_rate:.2f}%")

        # Calculate increase (percentage points)
        increase = current_rate - previous_rate
        logger.info(f"SRSService: Retention rate increase: {increase:.2f} percentage points")

        # Return as integer percentage point increase
        result = int(increase) if previous_rate > 0 else 0
        logger.info(f"SRSService: Returning retention increase: {result}%")
        return result

    def count_consecutive_perfect_reviews(self):
        """Count the number of consecutive perfect reviews (rating 4-5) in the most recent history."""
        logger.info("SRSService: Counting consecutive perfect reviews")
        # Get all review history ordered by time, most recent first
        history = ReviewHistory.query.order_by(ReviewHistory.created_at.desc()).all()
        logger.info(f"SRSService: Found {len(history)} total reviews in history")

        # Count consecutive perfect reviews
        consecutive_count = 0
        for review in history:
            if review.rating >= 4:  # Ratings 4-5 are considered "perfect"
                consecutive_count += 1
                logger.info(f"SRSService: Review {review.id} was perfect (rating {review.rating})")
            else:
                # Stop counting as soon as we hit a non-perfect review
                logger.info(f"SRSService: Found non-perfect review {review.id} (rating {review.rating}), stopping count")
                break

        logger.info(f"SRSService: Total consecutive perfect reviews: {consecutive_count}")
        return consecutive_count

    def get_learning_progress_data(self, months=7):
        """
        Get historical learning progress data for charts.

        Args:
            months: Number of past months to include in the data

        Returns:
            Dictionary with labels and datasets for charting
        """
        logger.info(f"SRSService: Getting learning progress data for past {months} months")
        # Create month labels based on current month
        now = datetime.now(ZoneInfo("UTC"))
        labels = []

        for i in range(months):
            # Calculate month by going backward from current month
            month_date = now.replace(day=1) - timedelta(days=30 * i)
            month_name = month_date.strftime("%b")
            labels.insert(0, month_name)  # Insert at beginning to get chronological order
            logger.info(f"SRSService: Added month label: {month_name}")

        # For now, use sample data similar to what's in the dashboard route
        # In a production environment, this would be calculated from actual database records

        # Sample data (these would ideally be calculated from ReviewHistory)
        mastered = [5, 9, 12, 18, 22, 28, 35][:months]
        added = [8, 12, 15, 20, 25, 30, 47][:months]
        retention = [60, 65, 70, 72, 75, 80, 83][:months]

        logger.info(f"SRSService: Sample data - Mastered: {mastered}")
        logger.info(f"SRSService: Sample data - Added: {added}")
        logger.info(f"SRSService: Sample data - Retention: {retention}")

        # Create datasets
        datasets = [
            {"label": "Cards Mastered", "data": mastered},
            {"label": "Cards Added", "data": added},
            {"label": "Retention Score", "data": retention},
        ]

        result = {"labels": labels, "datasets": datasets}
        logger.info("SRSService: Returning learning progress data")
        return result

    def get_cards_by_learning_stage(self, stage="new"):
        """
        Get cards filtered by their learning stage based on interval.

        Args:
            stage (str): One of 'new', 'learning', 'reviewing', or 'mastered'

        Returns:
            list: Cards in the specified learning stage
        """
        logger.info(f"SRSService: Retrieving cards in learning stage: {stage}")

        if stage == "new":
            # Cards that have never been reviewed
            logger.info("SRSService: Querying for new cards (review_count = 0)")
            cards = SRS.query.filter(SRS.review_count == 0).all()
        elif stage == "learning":
            # Cards in initial learning phase (interval <= 1 day but reviewed at least once)
            logger.info("SRSService: Querying for learning cards (review_count > 0, interval <= 1.0)")
            cards = SRS.query.filter(SRS.review_count > 0, SRS.interval <= 1.0).all()
        elif stage == "reviewing":
            # Cards in review phase (interval between 1 and 21 days)
            logger.info("SRSService: Querying for reviewing cards (1.0 < interval <= 21.0)")
            cards = SRS.query.filter(SRS.interval > 1.0, SRS.interval <= 21.0).all()
        elif stage == "mastered":
            # Cards considered mastered (interval > 21 days)
            logger.info("SRSService: Querying for mastered cards (interval > 21.0)")
            cards = SRS.query.filter(SRS.interval > 21.0).all()
        else:
            logger.error(f"SRSService: Unknown learning stage: {stage}")
            raise ValueError(f"Unknown learning stage: {stage}")

        logger.info(f"SRSService: Found {len(cards)} cards in {stage} stage")
        return cards

    def get_cards_by_difficulty(self, difficulty="easy"):
        """
        Get cards filtered by difficulty based on ease factor.

        Args:
            difficulty (str): One of 'hard', 'medium', or 'easy'

        Returns:
            list: Cards with the specified difficulty
        """
        logger.info(f"SRSService: Retrieving cards with difficulty: {difficulty}")

        if difficulty == "hard":
            # Hard cards (low ease factor)
            logger.info("SRSService: Querying for hard cards (ease_factor <= 1.5)")
            cards = SRS.query.filter(SRS.ease_factor <= 1.5, SRS.review_count > 0).all()  # Only include reviewed cards
        elif difficulty == "medium":
            # Medium difficulty cards
            logger.info("SRSService: Querying for medium cards (1.5 < ease_factor < 2.0)")
            cards = SRS.query.filter(SRS.ease_factor > 1.5, SRS.ease_factor < 2.0, SRS.review_count > 0).all()
        elif difficulty == "easy":
            # Easy cards (high ease factor)
            logger.info("SRSService: Querying for easy cards (ease_factor >= 2.0)")
            cards = SRS.query.filter(SRS.ease_factor >= 2.0, SRS.review_count > 0).all()
        else:
            logger.error(f"SRSService: Unknown difficulty: {difficulty}")
            raise ValueError(f"Unknown difficulty: {difficulty}")

        logger.info(f"SRSService: Found {len(cards)} cards with {difficulty} difficulty")
        return cards

    def get_cards_by_performance(self, performance="struggling"):
        """
        Get cards filtered by user performance.

        Args:
            performance (str): One of 'struggling', 'average', or 'strong'

        Returns:
            list: Cards that match the specified performance criteria
        """
        logger.info(f"SRSService: Retrieving cards with user performance: {performance}")

        # Join with review history to calculate statistics
        if performance == "struggling":
            # Cards with low success rate (< 60% correct)
            logger.info("SRSService: Querying for struggling cards (success rate < 60%)")
            cards = SRS.query.filter(SRS.review_count > 2, (SRS.successful_reps * 100 / SRS.review_count) < 60).all()  # At least 3 reviews
        elif performance == "average":
            # Cards with average success rate (60-85%)
            logger.info("SRSService: Querying for average performance cards (60% <= success rate <= 85%)")
            cards = SRS.query.filter(
                SRS.review_count > 2,
                (SRS.successful_reps * 100 / SRS.review_count) >= 60,
                (SRS.successful_reps * 100 / SRS.review_count) <= 85,
            ).all()
        elif performance == "strong":
            # Cards with high success rate (> 85%)
            logger.info("SRSService: Querying for strong performance cards (success rate > 85%)")
            cards = SRS.query.filter(SRS.review_count > 2, (SRS.successful_reps * 100 / SRS.review_count) > 85).all()
        else:
            logger.error(f"SRSService: Unknown performance level: {performance}")
            raise ValueError(f"Unknown performance level: {performance}")

        logger.info(f"SRSService: Found {len(cards)} cards with {performance} performance")
        return cards

    def get_review_strategy(self, strategy_name, limit=None):
        """
        Get cards based on various predefined review strategies.

        Args:
            strategy_name (str): Name of the review strategy
            limit (int): Optional maximum number of cards to return

        Returns:
            list: Cards that match the strategy criteria
        """
        logger.info(f"SRSService: Getting cards using review strategy: {strategy_name}, limit: {limit}")
        cards = []

        if strategy_name == "due_mix":
            # A mix of cards from different categories that are due
            logger.info("SRSService: Applying 'due_mix' strategy")
            due_cards = self.get_due_items()
            categories = {}

            # Group by category
            for card in due_cards:
                if card.notable_type not in categories:
                    categories[card.notable_type] = []
                categories[card.notable_type].append(card)

            logger.info(f"SRSService: Found cards in {len(categories)} categories: {list(categories.keys())}")

            # Get a mix of cards from each category
            for category, category_cards in categories.items():
                # Take about 1/3 of cards from each category, but at least 1
                category_limit = max(1, len(category_cards) // 3)
                logger.info(f"SRSService: Taking {category_limit} cards from category '{category}'")
                cards.extend(category_cards[:category_limit])

        elif strategy_name == "priority_first":
            # Cards that are most overdue first
            logger.info("SRSService: Applying 'priority_first' strategy (most overdue first)")
            cards = (
                SRS.query.filter(SRS.next_review_at.isnot(None), SRS.next_review_at <= datetime.now(ZoneInfo("UTC")))
                .order_by(SRS.next_review_at)
                .all()
            )

        elif strategy_name == "hard_cards_first":
            # Focus on difficult cards first
            logger.info("SRSService: Applying 'hard_cards_first' strategy (ease_factor <= 1.7)")
            cards = (
                SRS.query.filter(
                    SRS.next_review_at.isnot(None), SRS.next_review_at <= datetime.now(ZoneInfo("UTC")), SRS.ease_factor <= 1.7
                )
                .order_by(SRS.ease_factor)
                .all()
            )

        elif strategy_name == "mastery_boost":
            # Cards that are close to mastery (interval between 15-21 days)
            logger.info("SRSService: Applying 'mastery_boost' strategy (interval between 15-21 days)")
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
            logger.info("SRSService: Applying 'struggling_focus' strategy (success rate < 70%)")
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
            logger.info("SRSService: Applying 'new_mix' strategy (mix of new and due cards)")
            new_cards = SRS.query.filter(SRS.review_count == 0).limit(5).all()
            logger.info(f"SRSService: Found {len(new_cards)} new cards")

            due_cards = (
                SRS.query.filter(SRS.next_review_at.isnot(None), SRS.next_review_at <= datetime.now(ZoneInfo("UTC")), SRS.review_count > 0)
                .limit(10)
                .all()
            )
            logger.info(f"SRSService: Found {len(due_cards)} due cards")

            cards = new_cards + due_cards

        else:
            logger.error(f"SRSService: Unknown review strategy: {strategy_name}")
            raise ValueError(f"Unknown review strategy: {strategy_name}")

        # Apply limit if specified
        if limit:
            logger.info(f"SRSService: Limiting result to {limit} cards")
            cards = cards[:limit]

        logger.info(f"SRSService: Strategy '{strategy_name}' returned {len(cards)} cards")
        return cards

    def get_due_cards(self, limit=None):
        """
        Get SRS items that are due for review.

        Args:
            limit: Optional maximum number of cards to return

        Returns:
            List of SRS items due for review
        """
        logger.info(f"SRSService: Getting due cards with limit: {limit}")
        due_items = self.get_due_items()
        logger.info(f"SRSService: Found {len(due_items)} due items")

        if limit is not None:
            logger.info(f"SRSService: Limiting to {limit} items")
            return due_items[:limit]

        return due_items

    def calculate_progress_by_type(self, type_name=None):
        """
        Calculate the learning progress for cards of a specific type.

        Progress is calculated as the percentage of successful repetitions out of total reviews.
        If type_name is provided, calculate only for that type.
        Otherwise, return a dict with progress for all types.
        """
        if type_name:
            logger.info(f"SRSService: Calculating progress for type: {type_name}")
        else:
            logger.info("SRSService: Calculating progress for all types")

        all_items = self.get_all()

        def calculate_progress(cards):
            if not cards:
                return 0
            total_progress = sum((item.successful_reps or 0) / max(item.review_count or 1, 1) * 100 for item in cards)
            return int(total_progress / len(cards)) if cards else 0

        if type_name:
            # Filter items by type
            type_items = [item for item in all_items if item.notable_type == type_name]
            logger.info(f"SRSService: Found {len(type_items)} items of type '{type_name}'")
            progress = calculate_progress(type_items)
            logger.info(f"SRSService: Progress for type '{type_name}': {progress}%")
            return progress
        else:
            # Calculate progress for each type
            company_items = [item for item in all_items if item.notable_type == "company"]
            contact_items = [item for item in all_items if item.notable_type == "contact"]
            opportunity_items = [item for item in all_items if item.notable_type == "opportunity"]

            logger.info(
                f"SRSService: Found {len(company_items)} company items, {len(contact_items)} contact items, {len(opportunity_items)} opportunity items"
            )

            progress = {
                "company": calculate_progress(company_items),
                "contact": calculate_progress(contact_items),
                "opportunity": calculate_progress(opportunity_items),
                "overall": calculate_progress(all_items),
            }

            logger.info(f"SRSService: Progress by type: {progress}")
            return progress

    def count_due_by_type(self, type_name=None):
        """
        Count SRS items that are due for review, grouped by notable_type.

        If type_name is provided, count only due items of that type.
        Otherwise, return a dict with counts for all types.
        """
        # Get all due items
        logger.info("SRSService: Counting due items by type")
        due_items = self.get_due_items()
        logger.info(f"SRSService: Found {len(due_items)} total due items")

        if type_name:
            logger.info(f"SRSService: Counting due items for specific type: {type_name}")
            # Count due items of the specific type
            count = sum(1 for item in due_items if item.notable_type == type_name)
            logger.info(f"SRSService: Found {count} due items of type '{type_name}'")
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

            logger.info(f"SRSService: Due items by type: {counts}")
            return counts

    def count_by_type(self, type_name=None):
        """
        Count SRS items grouped by notable_type.

        If type_name is provided, count only items of that type.
        Otherwise, return a dict with counts for all types.
        """
        logger.info("SRSService: Counting all items by type")
        all_items = self.get_all()

        if type_name:
            logger.info(f"SRSService: Counting items for specific type: {type_name}")
            # Count items of the specific type
            count = sum(1 for item in all_items if item.notable_type == type_name)
            logger.info(f"SRSService: Found {count} items of type '{type_name}'")
            return count
        else:
            # Initialize counts dictionary
            counts = {"company": 0, "contact": 0, "opportunity": 0, "other": 0}  # For any items with unrecognized types

            # Count items by type
            for item in all_items:
                item_type = item.notable_type
                if item_type in counts:
                    counts[item_type] += 1
                else:
                    counts["other"] += 1

            logger.info(f"SRSService: Items by type: {counts}")
            return counts

    def get_stats(self):
        """Get current SRS system statistics."""
        logger.info("SRSService: Getting system statistics")
        total = SRS.query.count()
        logger.info(f"SRSService: Total cards: {total}")

        due_today = SRS.query.filter(SRS.next_review_at <= datetime.now(ZoneInfo("UTC"))).count()
        logger.info(f"SRSService: Cards due today: {due_today}")

        today_start = datetime.now(ZoneInfo("UTC")).replace(hour=0, minute=0, second=0, microsecond=0)
        reviewed_today = ReviewHistory.query.filter(ReviewHistory.created_at >= today_start).count()
        logger.info(f"SRSService: Cards reviewed today: {reviewed_today}")

        stats = {"total_cards": total, "cards_due": due_today, "cards_reviewed_today": reviewed_today}
        logger.info(f"SRSService: Returning statistics: {stats}")
        return stats

    def get_categories(self):
        """Get all available categories (decks)."""
        logger.info("SRSService: Getting all categories")
        # First get all distinct notable_types from the database
        query = db.session.query(SRS.notable_type).distinct()
        db_categories = [row[0] for row in query.all() if row[0]]
        logger.info(f"SRSService: Found {len(db_categories)} distinct categories in database: {db_categories}")

        # Get category counts
        category_counts = self.count_by_type()
        logger.info(f"SRSService: Category counts: {category_counts}")

        # Merge with predefined categories
        predefined = {
            "company": {"name": "Companies", "color": "primary", "icon": "building"},
            "contact": {"name": "Contacts", "color": "success", "icon": "people"},
            "opportunity": {"name": "Opportunities", "color": "danger", "icon": "graph-up-arrow"},
        }
        logger.info(f"SRSService: Using predefined categories: {list(predefined.keys())}")

        result = []

        # Add predefined categories first
        for category_id, info in predefined.items():
            count = category_counts.get(category_id, 0)
            result.append({"id": category_id, "name": info["name"], "color": info["color"], "icon": info["icon"], "count": count})
            logger.info(f"SRSService: Added predefined category: {category_id} with count {count}")

        # Add custom categories from database that aren't in predefined list
        for category_id in db_categories:
            if category_id not in predefined:
                count = category_counts.get(category_id, 0)
                result.append(
                    {
                        "id": category_id,
                        "name": category_id.capitalize(),  # Default name is capitalized ID
                        "color": "secondary",  # Default color
                        "icon": "folder",  # Default icon
                        "count": count,
                    }
                )
                logger.info(f"SRSService: Added custom category: {category_id} with count {count}")

        logger.info(f"SRSService: Returning {len(result)} total categories")
        return result

    def create_category(self, name, color="secondary", icon="folder"):
        """
        Create a new category (deck).

        This doesn't actually create a database record since categories
        are stored as notable_type strings on SRS items. Instead, it
        ensures the category ID is valid and returns a category object.
        """
        logger.info(f"SRSService: Creating category with name '{name}', color '{color}', icon '{icon}'")

        # Normalize the name to create a valid ID
        category_id = name.lower().replace(" ", "_")
        logger.info(f"SRSService: Normalized category ID: {category_id}")

        logger.info(f"SRSService: Creating category {category_id} with name '{name}'")

        # Return a category object
        result = {"id": category_id, "name": name, "color": color, "icon": icon, "count": 0}
        logger.info(f"SRSService: Created category object: {result}")
        return result

    def create(self, data):
        """Create a new SRS item."""
        logger.info(f"SRSService: Creating new SRS item with data: {data}")
        item = SRS()
        for key, value in data.items():
            setattr(item, key, value)
        item.save()
        logger.info(f"SRSService: Created new SRS item with ID {item.id}")
        return item

    def count_reviews_today(self):
        """Count the number of reviews completed today."""
        logger.info("SRSService: Counting reviews completed today")
        today_start = datetime.now(ZoneInfo("UTC")).replace(hour=0, minute=0, second=0, microsecond=0)
        logger.info(f"SRSService: Today started at {today_start.isoformat()}")

        count = ReviewHistory.query.filter(ReviewHistory.created_at >= today_start).count()
        logger.info(f"SRSService: Found {count} reviews completed today")
        return count

    def get_detailed_stats(self):
        """Get detailed learning statistics for analysis."""
        logger.info("SRSService: Getting detailed statistics")
        basic_stats = self.get_stats()
        logger.info(f"SRSService: Basic stats: {basic_stats}")

        all_cards = self.get_all()
        logger.info(f"SRSService: Found {len(all_cards)} total cards")

        logger.info("SRSService: Calculating learning stage counts")
        learning_stages = {
            "new": len(self.get_cards_by_learning_stage("new")),
            "learning": len(self.get_cards_by_learning_stage("learning")),
            "reviewing": len(self.get_cards_by_learning_stage("reviewing")),
            "mastered": len(self.get_cards_by_learning_stage("mastered")),
        }
        logger.info(f"SRSService: Learning stages: {learning_stages}")

        logger.info("SRSService: Calculating difficulty counts")
        difficulty_counts = {
            "hard": len(self.get_cards_by_difficulty("hard")),
            "medium": len(self.get_cards_by_difficulty("medium")),
            "easy": len(self.get_cards_by_difficulty("easy")),
        }
        logger.info(f"SRSService: Difficulty counts: {difficulty_counts}")

        logger.info("SRSService: Calculating performance counts")
        performance_counts = {
            "struggling": len(self.get_cards_by_performance("struggling")),
            "average": len(self.get_cards_by_performance("average")),
            "strong": len(self.get_cards_by_performance("strong")),
        }
        logger.info(f"SRSService: Performance counts: {performance_counts}")

        logger.info("SRSService: Calculating average values")
        avg_ease = sum(card.ease_factor or DEFAULT_EASE_FACTOR for card in all_cards) / len(all_cards) if all_cards else DEFAULT_EASE_FACTOR
        avg_interval = sum(card.interval or 0 for card in all_cards) / len(all_cards) if all_cards else 0
        logger.info(f"SRSService: Average ease factor: {avg_ease:.2f}, average interval: {avg_interval:.2f}")

        streak_days = self.get_streak_days()
        weekly_reviews = self.count_weekly_reviews()
        mastered_this_month = self.count_mastered_cards_this_month()

        logger.info(f"SRSService: Streak days: {streak_days}, weekly reviews: {weekly_reviews}, mastered this month: {mastered_this_month}")

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

        logger.info("SRSService: Returning detailed statistics")
        return stats

    def get_by_type(self, type_name):
        """Get all SRS items of a specific type."""
        logger.info(f"SRSService: Getting all items of type '{type_name}'")
        items = SRS.query.filter(SRS.notable_type == type_name).all()
        logger.info(f"SRSService: Found {len(items)} items of type '{type_name}'")
        return items

    def get_learning_stages_counts(self):
        """Get counts of cards by learning stage."""
        logger.info("SRSService: Getting counts by learning stage")
        counts = {
            "new": len(self.get_cards_by_learning_stage("new")),
            "learning": len(self.get_cards_by_learning_stage("learning")),
            "reviewing": len(self.get_cards_by_learning_stage("reviewing")),
            "mastered": len(self.get_cards_by_learning_stage("mastered")),
        }
        logger.info(f"SRSService: Learning stage counts: {counts}")
        return counts

    def get_difficulty_counts(self):
        """Get counts of cards by difficulty level."""
        logger.info("SRSService: Getting counts by difficulty level")
        counts = {
            "hard": len(self.get_cards_by_difficulty("hard")),
            "medium": len(self.get_cards_by_difficulty("medium")),
            "easy": len(self.get_cards_by_difficulty("easy")),
        }
        logger.info(f"SRSService: Difficulty counts: {counts}")
        return counts

    def get_performance_counts(self):
        """Get counts of cards by performance level."""
        logger.info("SRSService: Getting counts by performance level")
        counts = {
            "struggling": len(self.get_cards_by_performance("struggling")),
            "average": len(self.get_cards_by_performance("average")),
            "strong": len(self.get_cards_by_performance("strong")),
        }
        logger.info(f"SRSService: Performance counts: {counts}")
        return counts
