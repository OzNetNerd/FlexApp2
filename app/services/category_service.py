# app/services/category_service.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# from app.models.pages.srs import Category, SRS
from app.utils.app_logging import get_logger

logger = get_logger()


class CategoryService:
    """Service for managing SRS card categories."""

    def __init__(self):
        """Initialize the Category service."""
        pass

    def get_by_id(self, category_id):
        """Get a category by ID."""
        return Category.query.get(category_id)

    def get_all(self):
        """Get all categories."""
        return Category.query.all()

    def get_all_with_counts(self):
        """Get all categories with card counts."""
        categories = self.get_all()
        result = []

        for category in categories:
            total_count = len(category.cards) if category.cards else 0
            due_count = sum(1 for card in category.cards if card.next_review_at and card.next_review_at <= datetime.now(ZoneInfo("UTC")))

            result.append(
                {
                    "id": category.id,
                    "name": category.name,
                    "color": category.color,
                    "icon": category.icon,
                    "total": total_count,
                    "due": due_count,
                    "progress": self._calculate_progress(category.cards),
                }
            )

        return result

    def _calculate_progress(self, cards):
        """Calculate learning progress for a list of cards."""
        if not cards:
            return 0

        total_progress = sum((card.successful_reps or 0) / max(card.review_count or 1, 1) * 100 for card in cards)
        return int(total_progress / len(cards))

    def get_counts(self):
        """Get counts of cards by category."""
        categories = self.get_all()
        return {category.id: len(category.cards) if category.cards else 0 for category in categories}

    def create(self, data):
        """Create a new category."""
        category = Category()
        for key, value in data.items():
            setattr(category, key, value)
        category.save()
        return category

    def update(self, category, data):
        """Update a category."""
        for key, value in data.items():
            setattr(category, key, value)
        category.save()
        return category

    def delete(self, category_id):
        """Delete a category."""
        category = self.get_by_id(category_id)
        if category:
            category.delete()
            return True
        return False
