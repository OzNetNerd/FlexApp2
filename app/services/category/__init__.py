# app/services/category/__init__.py
from app.services.service_base import ServiceBase, ServiceRegistry
from app.services.category.core import CategoryCoreService
from app.services.category.analytics import CategoryAnalyticsService


class CategoryService(ServiceBase):
    """Main service for managing SRS card categories."""

    def __init__(self):
        """Initialize the Category service with sub-services."""
        super().__init__()
        self.core = ServiceRegistry.get(CategoryCoreService)
        self.analytics = ServiceRegistry.get(CategoryAnalyticsService)

    # Core CRUD operations - delegate to core service
    def get_by_id(self, category_id):
        """Get a category by ID."""
        return self.core.get_by_id(category_id)

    def get_all(self):
        """Get all categories."""
        return self.core.get_all()

    def create(self, data):
        """Create a new category."""
        return self.core.create(data)

    def update(self, category, data):
        """Update a category."""
        return self.core.update(category, data)

    def delete(self, category_id):
        """Delete a category."""
        return self.core.delete(category_id)

    # Analytics operations - delegate to analytics service
    def get_all_with_counts(self):
        """Get all categories with card counts."""
        categories = self.get_all()
        return self.analytics.get_all_with_counts(categories)

    def get_counts(self):
        """Get counts of cards by category."""
        categories = self.get_all()
        return self.analytics.get_counts(categories)