from datetime import datetime, UTC, timedelta
from app.models.pages.srs import SRS, ReviewHistory
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

    def get_filtered_cards(self, filters=None):
        """Get SRS cards filtered by various criteria."""
        # Start with base query
        query = SRS.query

        # Apply filters if provided
        if filters:
            # Due cards filter
            if filters.get('due_only'):
                query = query.filter(SRS.next_review_at <= datetime.now(UTC))

            # Category filter
            if filters.get('category'):
                query = query.filter(SRS.notable_type == filters['category'])

            # Text search in question or answer
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    (SRS.question.ilike(search_term)) |
                    (SRS.answer.ilike(search_term))
                )

            # Interval range
            if filters.get('min_interval') is not None:
                query = query.filter(SRS.interval >= filters['min_interval'])
            if filters.get('max_interval') is not None:
                query = query.filter(SRS.interval <= filters['max_interval'])

            # Ease factor range
            if filters.get('min_ease') is not None:
                query = query.filter(SRS.ease_factor >= filters['min_ease'])
            if filters.get('max_ease') is not None:
                query = query.filter(SRS.ease_factor <= filters['max_ease'])

            # Sort order
            sort_field = getattr(SRS, filters.get('sort_by', 'next_review_at'))
            if filters.get('sort_order') == 'desc':
                sort_field = sort_field.desc()
            query = query.order_by(sort_field)

        # Execute query
        return query.all()

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

    def get_categories(self):
        """Get all available categories (decks)."""
        # First get all distinct notable_types from the database
        query = db.session.query(SRS.notable_type).distinct()
        db_categories = [row[0] for row in query.all() if row[0]]

        # Get category counts
        category_counts = self.count_by_type()

        # Merge with predefined categories
        predefined = {
            'company': {'name': 'Companies', 'color': 'primary', 'icon': 'building'},
            'contact': {'name': 'Contacts', 'color': 'success', 'icon': 'people'},
            'opportunity': {'name': 'Opportunities', 'color': 'danger', 'icon': 'graph-up-arrow'}
        }

        result = []

        # Add predefined categories first
        for category_id, info in predefined.items():
            count = category_counts.get(category_id, 0)
            result.append({
                'id': category_id,
                'name': info['name'],
                'color': info['color'],
                'icon': info['icon'],
                'count': count
            })

        # Add custom categories from database that aren't in predefined list
        for category_id in db_categories:
            if category_id not in predefined:
                count = category_counts.get(category_id, 0)
                result.append({
                    'id': category_id,
                    'name': category_id.capitalize(),  # Default name is capitalized ID
                    'color': 'secondary',  # Default color
                    'icon': 'folder',  # Default icon
                    'count': count
                })

        return result


    def create_category(self, name, color='secondary', icon='folder'):
        """
        Create a new category (deck).

        This doesn't actually create a database record since categories
        are stored as notable_type strings on SRS items. Instead, it
        ensures the category ID is valid and returns a category object.
        """
        # Normalize the name to create a valid ID
        category_id = name.lower().replace(' ', '_')

        logger.info(f"SRSService: Creating category {category_id} with name '{name}'")

        # Return a category object
        return {
            'id': category_id,
            'name': name,
            'color': color,
            'icon': icon,
            'count': 0
        }


    def create(self, data):
        """Create a new SRS item."""
        item = SRS()
        for key, value in data.items():
            setattr(item, key, value)
        item.save()
        return item


    def count_reviews_today(self):
        """Count the number of reviews completed today."""
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        return ReviewHistory.query.filter(
            ReviewHistory.timestamp >= today_start
        ).count()

    def get_detailed_stats(self):
        """Get detailed learning statistics for analysis."""
        basic_stats = self.get_stats()
        all_cards = self.get_all()

        learning_stages = {
            'new': len(self.get_cards_by_learning_stage('new')),
            'learning': len(self.get_cards_by_learning_stage('learning')),
            'reviewing': len(self.get_cards_by_learning_stage('reviewing')),
            'mastered': len(self.get_cards_by_learning_stage('mastered'))
        }

        difficulty_counts = {
            'hard': len(self.get_cards_by_difficulty('hard')),
            'medium': len(self.get_cards_by_difficulty('medium')),
            'easy': len(self.get_cards_by_difficulty('easy'))
        }

        performance_counts = {
            'struggling': len(self.get_cards_by_performance('struggling')),
            'average': len(self.get_cards_by_performance('average')),
            'strong': len(self.get_cards_by_performance('strong'))
        }

        stats = {
            **basic_stats,
            'average_ease_factor': sum(card.ease_factor or DEFAULT_EASE_FACTOR for card in all_cards) / len(
                all_cards) if all_cards else DEFAULT_EASE_FACTOR,
            'average_interval': sum(card.interval or 0 for card in all_cards) / len(all_cards) if all_cards else 0,
            'learning_stages': learning_stages,
            'difficulty_counts': difficulty_counts,
            'performance_counts': performance_counts,
            'streak_days': self.get_streak_days(),
            'weekly_reviews': self.count_weekly_reviews(),
            'mastered_this_month': self.count_mastered_cards_this_month()
        }

        return stats

    def get_by_type(self, type_name):
        """Get all SRS items of a specific type."""
        return SRS.query.filter(SRS.notable_type == type_name).all()

    def get_learning_stages_counts(self):
        """Get counts of cards by learning stage."""
        return {
            'new': len(self.get_cards_by_learning_stage('new')),
            'learning': len(self.get_cards_by_learning_stage('learning')),
            'reviewing': len(self.get_cards_by_learning_stage('reviewing')),
            'mastered': len(self.get_cards_by_learning_stage('mastered'))
        }

    def get_difficulty_counts(self):
        """Get counts of cards by difficulty level."""
        return {
            'hard': len(self.get_cards_by_difficulty('hard')),
            'medium': len(self.get_cards_by_difficulty('medium')),
            'easy': len(self.get_cards_by_difficulty('easy'))
        }

    def get_performance_counts(self):
        """Get counts of cards by performance level."""
        return {
            'struggling': len(self.get_cards_by_performance('struggling')),
            'average': len(self.get_cards_by_performance('average')),
            'strong': len(self.get_cards_by_performance('strong'))
        }