# app/services/category/analytics.py
from datetime import datetime
from zoneinfo import ZoneInfo
from app.services.service_base import ServiceBase
from app.utils.app_logging import get_logger

logger = get_logger()


class CategoryAnalyticsService(ServiceBase):
    """Service for category analytics and statistics."""

    def __init__(self):
        """Initialize the Category analytics service."""
        super().__init__()

    def get_all_with_counts(self, categories):
        """Calculate statistics for all categories."""
        result = []

        for category in categories:
            total_count = len(category.cards) if category.cards else 0
            due_count = sum(1 for card in category.cards if card.next_review_at and
                           card.next_review_at <= datetime.now(ZoneInfo("UTC")))

            result.append({
                "id": category.id,
                "name": category.name,
                "color": category.color,
                "icon": category.icon,
                "total": total_count,
                "due": due_count,
                "progress": self.calculate_progress(category.cards),
            })

        return result

    def calculate_progress(self, cards):
        """Calculate learning progress for a list of cards."""
        if not cards:
            return 0

        total_progress = sum((card.successful_reps or 0) / max(card.review_count or 1, 1) * 100 for card in cards)
        return int(total_progress / len(cards))

    def get_counts(self, categories):
        """Get counts of cards by category."""
        return {category.id: len(category.cards) if category.cards else 0 for category in categories}