from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, UTC, timedelta
from app.models.pages.srs import SRS, ReviewHistory
from app.routes.web.blueprint_factory import create_crud_blueprint
from app.utils.app_logging import get_logger

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
        pass

    def get_by_id(self, item_id: int) -> SRS:
        """Get an SRS item by ID."""
        return SRS.query.get(item_id)

    def get_all(self) -> list:
        """Get all SRS items."""
        return SRS.query.all()

    def update(self, item, update_data):
        """Update an SRS item."""
        for key, value in update_data.items():
            setattr(item, key, value)
        item.save()
        return item

    def preview_ratings(self, item_id: int) -> dict:
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

    def count_total(self):
        """Get the total count of SRS items."""
        return SRS.query.count()

    def count_due_today(self):
        """Get the count of SRS items due for review today."""
        return SRS.query.filter(
            SRS.next_review_at <= datetime.now(UTC)
        ).count()

    def calculate_success_rate(self):
        """Calculate the success rate of SRS items as a percentage."""
        all_items = self.get_all()
        if not all_items:
            return 0

        successful_items = sum(
            1 for item in all_items
            if item.successful_reps and item.review_count and item.review_count > 0
        )

        return int((successful_items / len(all_items)) * 100) if len(all_items) > 0 else 0

    def get_due_items(self) -> list:
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

    def get_streak_days(self):
        """Calculate the current streak of consecutive days with SRS reviews."""
        # Get dates with activity
        today = datetime.now(UTC).date()
        history_dates = set(
            h.timestamp.date()
            for h in ReviewHistory.query.all()
        )

        if not history_dates:
            return 0

        # Calculate streak
        streak = 0
        current_date = today

        # Check if there was activity today
        if today in history_dates:
            streak = 1
            current_date = today - timedelta(days=1)
        else:
            # If no activity today, check yesterday
            yesterday = today - timedelta(days=1)
            if yesterday in history_dates:
                streak = 1
                current_date = yesterday - timedelta(days=1)
            else:
                return 0  # No streak

        # Check previous days
        while current_date in history_dates:
            streak += 1
            current_date = current_date - timedelta(days=1)

        return streak

    def count_mastered_cards_this_month(self):
        """Count the number of cards that became mastered this month."""
        # Define mastery threshold
        mastery_threshold = 30  # 30 days interval as mastery threshold

        # Get current month range
        now = datetime.now(UTC)
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Find cards that have reached mastery this month
        # We can determine this by looking at review history entries where the interval
        # crossed the mastery threshold during this month
        mastered_cards = 0

        # Get unique cards with reviews this month
        month_reviews = ReviewHistory.query.filter(
            ReviewHistory.timestamp >= first_of_month
        ).all()

        # Get unique card IDs with intervals crossing the threshold this month
        mastered_card_ids = set()
        for review in month_reviews:
            if review.interval >= mastery_threshold:
                # Check if this is the first time the card crossed the threshold
                prev_reviews = ReviewHistory.query.filter(
                    ReviewHistory.srs_item_id == review.srs_item_id,
                    ReviewHistory.timestamp < review.timestamp
                ).order_by(ReviewHistory.timestamp.desc()).first()

                # If no previous reviews or previous review had interval < threshold
                if not prev_reviews or prev_reviews.interval < mastery_threshold:
                    mastered_card_ids.add(review.srs_item_id)

        return len(mastered_card_ids)

    def count_weekly_reviews(self):
        """Count the number of reviews completed in the past 7 days."""
        now = datetime.now(UTC)
        week_ago = now - timedelta(days=7)

        return ReviewHistory.query.filter(
            ReviewHistory.timestamp >= week_ago,
            ReviewHistory.timestamp <= now
        ).count()

    def calculate_retention_increase(self):
        """Calculate the increase in retention rate over the past month compared to the previous month."""
        now = datetime.now(UTC)

        # Current month
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Previous month
        if current_month_start.month == 1:
            prev_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
        else:
            prev_month_start = current_month_start.replace(month=current_month_start.month - 1)

        # Get reviews for current and previous months
        current_month_reviews = ReviewHistory.query.filter(
            ReviewHistory.timestamp >= current_month_start,
            ReviewHistory.timestamp < now
        ).all()

        prev_month_reviews = ReviewHistory.query.filter(
            ReviewHistory.timestamp >= prev_month_start,
            ReviewHistory.timestamp < current_month_start
        ).all()

        # Calculate success rates
        def calc_success_rate(reviews):
            if not reviews:
                return 0
            successful = sum(1 for r in reviews if r.rating >= 3)
            return (successful / len(reviews)) * 100

        current_rate = calc_success_rate(current_month_reviews)
        previous_rate = calc_success_rate(prev_month_reviews)

        # Calculate increase (percentage points)
        increase = current_rate - previous_rate

        # Return as integer percentage point increase
        return int(increase) if previous_rate > 0 else 0

    def count_consecutive_perfect_reviews(self):
        """Count the number of consecutive perfect reviews (rating 4-5) in the most recent history."""
        # Get all review history ordered by time, most recent first
        history = ReviewHistory.query.order_by(
            ReviewHistory.timestamp.desc()
        ).all()

        # Count consecutive perfect reviews
        consecutive_count = 0
        for review in history:
            if review.rating >= 4:  # Ratings 4-5 are considered "perfect"
                consecutive_count += 1
            else:
                # Stop counting as soon as we hit a non-perfect review
                break

        return consecutive_count

    def get_learning_progress_data(self, months=7):
        """
        Get historical learning progress data for charts.

        Args:
            months: Number of past months to include in the data

        Returns:
            Dictionary with labels and datasets for charting
        """
        # Create month labels based on current month
        now = datetime.now(UTC)
        labels = []

        for i in range(months):
            # Calculate month by going backward from current month
            month_date = now.replace(day=1) - timedelta(days=30 * i)
            month_name = month_date.strftime('%b')
            labels.insert(0, month_name)  # Insert at beginning to get chronological order

        # For now, use sample data similar to what's in the dashboard route
        # In a production environment, this would be calculated from actual database records

        # Sample data (these would ideally be calculated from ReviewHistory)
        mastered = [5, 9, 12, 18, 22, 28, 35][:months]
        added = [8, 12, 15, 20, 25, 30, 47][:months]
        retention = [60, 65, 70, 72, 75, 80, 83][:months]

        # Create datasets
        datasets = [
            {'label': 'Cards Mastered', 'data': mastered},
            {'label': 'Cards Added', 'data': added},
            {'label': 'Retention Score', 'data': retention}
        ]

        return {
            'labels': labels,
            'datasets': datasets
        }

    def get_cards_by_learning_stage(self, stage='new'):
        """
        Get cards filtered by their learning stage based on interval.

        Args:
            stage (str): One of 'new', 'learning', 'reviewing', or 'mastered'

        Returns:
            list: Cards in the specified learning stage
        """
        if stage == 'new':
            # Cards that have never been reviewed
            return SRS.query.filter(SRS.review_count == 0).all()
        elif stage == 'learning':
            # Cards in initial learning phase (interval <= 1 day but reviewed at least once)
            return SRS.query.filter(
                SRS.review_count > 0,
                SRS.interval <= 1.0
            ).all()
        elif stage == 'reviewing':
            # Cards in review phase (interval between 1 and 21 days)
            return SRS.query.filter(
                SRS.interval > 1.0,
                SRS.interval <= 21.0
            ).all()
        elif stage == 'mastered':
            # Cards considered mastered (interval > 21 days)
            return SRS.query.filter(SRS.interval > 21.0).all()
        else:
            raise ValueError(f"Unknown learning stage: {stage}")

    def get_cards_by_difficulty(self, difficulty='easy'):
        """
        Get cards filtered by difficulty based on ease factor.

        Args:
            difficulty (str): One of 'hard', 'medium', or 'easy'

        Returns:
            list: Cards with the specified difficulty
        """
        if difficulty == 'hard':
            # Hard cards (low ease factor)
            return SRS.query.filter(
                SRS.ease_factor <= 1.5,
                SRS.review_count > 0  # Only include reviewed cards
            ).all()
        elif difficulty == 'medium':
            # Medium difficulty cards
            return SRS.query.filter(
                SRS.ease_factor > 1.5,
                SRS.ease_factor < 2.0,
                SRS.review_count > 0
            ).all()
        elif difficulty == 'easy':
            # Easy cards (high ease factor)
            return SRS.query.filter(
                SRS.ease_factor >= 2.0,
                SRS.review_count > 0
            ).all()
        else:
            raise ValueError(f"Unknown difficulty: {difficulty}")

    def get_cards_by_performance(self, performance='struggling'):
        """
        Get cards filtered by user performance.

        Args:
            performance (str): One of 'struggling', 'average', or 'strong'

        Returns:
            list: Cards that match the specified performance criteria
        """
        # Join with review history to calculate statistics
        if performance == 'struggling':
            # Cards with low success rate (< 60% correct)
            return SRS.query.filter(
                SRS.review_count > 2,  # At least 3 reviews
                (SRS.successful_reps * 100 / SRS.review_count) < 60
            ).all()
        elif performance == 'average':
            # Cards with average success rate (60-85%)
            return SRS.query.filter(
                SRS.review_count > 2,
                (SRS.successful_reps * 100 / SRS.review_count) >= 60,
                (SRS.successful_reps * 100 / SRS.review_count) <= 85
            ).all()
        elif performance == 'strong':
            # Cards with high success rate (> 85%)
            return SRS.query.filter(
                SRS.review_count > 2,
                (SRS.successful_reps * 100 / SRS.review_count) > 85
            ).all()
        else:
            raise ValueError(f"Unknown performance level: {performance}")

    def get_review_strategy(self, strategy_name, limit=None):
        """
        Get cards based on various predefined review strategies.

        Args:
            strategy_name (str): Name of the review strategy
            limit (int): Optional maximum number of cards to return

        Returns:
            list: Cards that match the strategy criteria
        """
        cards = []

        if strategy_name == 'due_mix':
            # A mix of cards from different categories that are due
            due_cards = self.get_due_items()
            categories = {}

            # Group by category
            for card in due_cards:
                if card.notable_type not in categories:
                    categories[card.notable_type] = []
                categories[card.notable_type].append(card)

            # Get a mix of cards from each category
            for category_cards in categories.values():
                # Take about 1/3 of cards from each category, but at least 1
                category_limit = max(1, len(category_cards) // 3)
                cards.extend(category_cards[:category_limit])

        elif strategy_name == 'priority_first':
            # Cards that are most overdue first
            cards = SRS.query.filter(
                SRS.next_review_at <= datetime.now(UTC)
            ).order_by(SRS.next_review_at).all()

        elif strategy_name == 'hard_cards_first':
            # Focus on difficult cards first
            cards = SRS.query.filter(
                SRS.next_review_at <= datetime.now(UTC),
                SRS.ease_factor <= 1.7
            ).order_by(SRS.ease_factor).all()

        elif strategy_name == 'mastery_boost':
            # Cards that are close to mastery (interval between 15-21 days)
            cards = SRS.query.filter(
                SRS.next_review_at <= datetime.now(UTC),
                SRS.interval >= 15,
                SRS.interval <= 21
            ).order_by(SRS.interval.desc()).all()

        elif strategy_name == 'struggling_focus':
            # Focus on cards with low success rate
            cards = SRS.query.filter(
                SRS.next_review_at <= datetime.now(UTC),
                SRS.review_count > 2,
                (SRS.successful_reps * 100 / SRS.review_count) < 70
            ).order_by((SRS.successful_reps * 100 / SRS.review_count)).all()

        elif strategy_name == 'new_mix':
            # Mix of new and due cards
            new_cards = SRS.query.filter(SRS.review_count == 0).limit(5).all()
            due_cards = SRS.query.filter(
                SRS.next_review_at <= datetime.now(UTC),
                SRS.review_count > 0
            ).limit(10).all()
            cards = new_cards + due_cards

        else:
            raise ValueError(f"Unknown review strategy: {strategy_name}")

        # Apply limit if specified
        if limit:
            cards = cards[:limit]

        return cards

    def get_due_cards(self, limit=None):
        """
        Get SRS items that are due for review.

        Args:
            limit: Optional maximum number of cards to return

        Returns:
            List of SRS items due for review
        """
        due_items = self.get_due_items()

        if limit is not None:
            return due_items[:limit]
        return due_items

    def calculate_progress_by_type(self, type_name=None):
        """
        Calculate the learning progress for cards of a specific type.

        Progress is calculated as the percentage of successful repetitions out of total reviews.
        If type_name is provided, calculate only for that type.
        Otherwise, return a dict with progress for all types.
        """
        all_items = self.get_all()


        def calculate_progress(cards):
            if not cards:
                return 0
            total_progress = sum((item.successful_reps or 0) / max(item.review_count or 1, 1) * 100 for item in cards)
            return int(total_progress / len(cards)) if cards else 0

        if type_name:
            # Filter items by type
            type_items = [item for item in all_items if item.notable_type == type_name]
            return calculate_progress(type_items)
        else:
            # Calculate progress for each type
            progress = {
                'company': calculate_progress([item for item in all_items if item.notable_type == 'company']),
                'contact': calculate_progress([item for item in all_items if item.notable_type == 'contact']),
                'opportunity': calculate_progress([item for item in all_items if item.notable_type == 'opportunity']),
                'overall': calculate_progress(all_items)
            }
            return progress

    def count_due_by_type(self, type_name=None):
        """
        Count SRS items that are due for review, grouped by notable_type.

        If type_name is provided, count only due items of that type.
        Otherwise, return a dict with counts for all types.
        """
        # Get all due items
        due_items = self.get_due_items()

        if type_name:
            # Count due items of the specific type
            return sum(1 for item in due_items if item.notable_type == type_name)
        else:
            # Initialize counts dictionary
            counts = {
                'company': 0,
                'contact': 0,
                'opportunity': 0,
                'other': 0  # For any items with unrecognized types
            }

            # Count due items by type
            for item in due_items:
                item_type = item.notable_type
                if item_type in counts:
                    counts[item_type] += 1
                else:
                    counts['other'] += 1

            return counts

    def count_by_type(self, type_name=None):
        """
        Count SRS items grouped by notable_type.

        If type_name is provided, count only items of that type.
        Otherwise, return a dict with counts for all types.
        """
        all_items = self.get_all()

        if type_name:
            # Count items of the specific type
            return sum(1 for item in all_items if item.notable_type == type_name)
        else:
            # Initialize counts dictionary
            counts = {
                'company': 0,
                'contact': 0,
                'opportunity': 0,
                'other': 0  # For any items with unrecognized types
            }

            # Count items by type
            for item in all_items:
                item_type = item.notable_type
                if item_type in counts:
                    counts[item_type] += 1
                else:
                    counts['other'] += 1

            return counts

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


# Create the service instance
srs_service = SRSService()

# Create a blueprint with CRUD operations
srs_bp = create_crud_blueprint(SRS, service=srs_service)


# Dashboard route
@srs_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """Render the flashcard dashboard."""
    # Get statistics from the service
    service_stats = srs_service.get_stats()

    # Count total cards in the database
    total_cards = service_stats.get('total_cards', 0)

    # Get cards due today
    due_today = service_stats.get('cards_due', 0)

    # Calculate basic success rate (if possible)
    success_rate = 0
    all_items = srs_service.get_all()
    if all_items:
        successful_items = sum(
            1 for item in all_items if item.successful_reps and item.review_count and item.review_count > 0)
        success_rate = int((successful_items / len(all_items)) * 100) if len(all_items) > 0 else 0

    # Fill in other stats with placeholder data for now
    stats = {
        'total_cards': total_cards,
        'due_today': due_today,
        'success_rate': success_rate,
        'days_streak': 9,  # Placeholder
        'weekly_reviews': service_stats.get('cards_reviewed_today', 0) * 7,  # Rough estimate
        'mastered_cards': 5,  # Placeholder
        'retention_increase': 18,  # Placeholder
        'perfect_reviews': 3  # Placeholder
    }

    # Get all cards to calculate category stats
    all_items = srs_service.get_all()

    # Count cards by type
    company_cards = [item for item in all_items if item.notable_type == 'company']
    contact_cards = [item for item in all_items if item.notable_type == 'contact']
    opportunity_cards = [item for item in all_items if item.notable_type == 'opportunity']

    # Simple progress calculation based on successful repetitions
    def calculate_progress(cards):
        if not cards:
            return 0
        total_progress = sum((item.successful_reps or 0) / max(item.review_count or 1, 1) * 100 for item in cards)
        return int(total_progress / len(cards)) if cards else 0

    # Get cards due today
    due_cards = srs_service.get_due_items()

    # Count due cards by type
    company_due = len([item for item in due_cards if item.notable_type == 'company'])
    contact_due = len([item for item in due_cards if item.notable_type == 'contact'])
    opportunity_due = len([item for item in due_cards if item.notable_type == 'opportunity'])

    # Create categories data
    categories = [
        {
            'name': 'Companies',
            'type': 'company',
            'icon': 'building',
            'color': 'primary',
            'total': len(company_cards),
            'due': company_due,
            'progress': calculate_progress(company_cards)
        },
        {
            'name': 'Contacts',
            'type': 'contact',
            'icon': 'people',
            'color': 'success',
            'total': len(contact_cards),
            'due': contact_due,
            'progress': calculate_progress(contact_cards)
        },
        {
            'name': 'Opportunities',
            'type': 'opportunity',
            'icon': 'graph-up-arrow',
            'color': 'danger',
            'total': len(opportunity_cards),
            'due': opportunity_due,
            'progress': calculate_progress(opportunity_cards)
        }
    ]

    # Get due cards for today (limited to 5 for display)
    due_cards = srs_service.get_due_items()[:5]

    # Create sample learning progress data for chart
    # In a real implementation, this would be calculated from ReviewHistory
    progress_data = {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        'datasets': [
            {
                'label': 'Cards Mastered',
                'data': [5, 9, 12, 18, 22, 28, 35]
            },
            {
                'label': 'Cards Added',
                'data': [8, 12, 15, 20, 25, 30, 47]
            },
            {
                'label': 'Retention Score',
                'data': [60, 65, 70, 72, 75, 80, 83]
            }
        ]
    }

    return render_template(
        "pages/srs/dashboard.html",
        stats=stats,
        categories=categories,
        due_cards=due_cards,
        progress_data=progress_data
    )


# Due cards route
@srs_bp.route("/due", methods=["GET"])
@login_required
def due_cards():
    """View all cards due for review today."""
    cards = srs_service.get_due_items()
    return render_template(
        "pages/srs/due.html",
        cards=cards,
        title="Cards Due Today"
    )


# Review card route
@srs_bp.route("/<int:item_id>/review", methods=["GET", "POST"])
@login_required
def review_item(item_id):
    """Web route for reviewing an SRS item."""
    item = srs_service.get_by_id(item_id)

    if not item:
        flash("Card not found", "error")
        return redirect(url_for('srs_bp.dashboard'))

    if request.method == "POST":
        rating = int(request.form.get("rating", 0))
        item = srs_service.schedule_review(item_id, rating)

        # Record review history
        history = ReviewHistory(
            srs_item_id=item_id,
            rating=rating,
            interval=item.interval,
            ease_factor=item.ease_factor
        )
        history.save()

        flash("Card reviewed successfully", "success")

        # If there are more due cards, go to the next one
        next_due = srs_service.get_next_due_item_id(item_id)
        if next_due:
            return redirect(url_for('srs_bp.review_item', item_id=next_due))
        else:
            return redirect(url_for('srs_bp.dashboard'))

    # Get navigation variables
    next_item_id = srs_service.get_next_due_item_id(item_id)
    prev_item_id = srs_service.get_prev_item_id(item_id)

    return render_template(
        "pages/srs/review.html",
        card=item,
        title="Review Card",
        next_item_id=next_item_id,
        prev_item_id=prev_item_id
    )


# Category view route
@srs_bp.route("/category/<string:category_type>", methods=["GET"])
@login_required
def category_view(category_type):
    """View cards by category."""
    # Filter cards by notable_type
    all_cards = srs_service.get_all()
    cards = [card for card in all_cards if card.notable_type == category_type]

    category_info = {
        'company': {'name': 'Companies', 'color': 'primary'},
        'contact': {'name': 'Contacts', 'color': 'success'},
        'opportunity': {'name': 'Opportunities', 'color': 'danger'}
    }

    info = category_info.get(category_type, {'name': 'Unknown', 'color': 'secondary'})

    return render_template(
        "pages/srs/category.html",
        cards=cards,
        category_type=category_type,
        category_name=info['name'],
        category_color=info['color'],
        title=f"{info['name']} Cards"
    )


# Statistics route
@srs_bp.route("/stats", methods=["GET"])
@login_required
def statistics():
    """View detailed learning statistics."""
    # Get basic stats from service
    basic_stats = srs_service.get_stats()

    # Get all cards and history for additional calculations
    all_cards = srs_service.get_all()

    # Build more detailed stats
    stats = {
        **basic_stats,
        'average_ease_factor': sum(card.ease_factor or DEFAULT_EASE_FACTOR for card in all_cards) / len(
            all_cards) if all_cards else DEFAULT_EASE_FACTOR,
        'average_interval': sum(card.interval or 0 for card in all_cards) / len(all_cards) if all_cards else 0,
        'mastered_cards': len([card for card in all_cards if card.interval and card.interval > 30]),
        'learning_cards': len(
            [card for card in all_cards if card.interval and card.interval <= 30 and card.interval > 1]),
        'new_cards': len([card for card in all_cards if card.review_count == 0])
    }

    return render_template(
        "pages/srs/stats.html",
        stats=stats,
        title="Learning Statistics"
    )


# API endpoint for chart data
@srs_bp.route("/api/progress-data", methods=["GET"])
@login_required
def progress_data():
    """Get progress data for charts."""
    months = request.args.get('months', 7, type=int)

    # Create sample data (in a real implementation, this would be calculated from ReviewHistory)
    data = {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'][:months],
        'datasets': [
            {
                'label': 'Cards Mastered',
                'data': [5, 9, 12, 18, 22, 28, 35][:months]
            },
            {
                'label': 'Cards Added',
                'data': [8, 12, 15, 20, 25, 30, 47][:months]
            },
            {
                'label': 'Retention Score',
                'data': [60, 65, 70, 72, 75, 80, 83][:months]
            }
        ]
    }

    return jsonify(data)


# Register the blueprint
def register_srs_blueprint(app):
    """Register the SRS blueprint with the app."""
    app.register_blueprint(srs_bp, url_prefix='/flashcards')