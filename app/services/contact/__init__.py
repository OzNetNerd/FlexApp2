# app/services/contact/__init__.py
from app.services.service_base import ServiceBase, ServiceRegistry
from app.services.contact.core import ContactCoreService
from app.services.contact.analytics import ContactAnalyticsService


class ContactService(ServiceBase):
    """Main service for managing contacts."""

    def __init__(self):
        """Initialize the Contact service with sub-services."""
        super().__init__()
        self.core = ServiceRegistry.get(ContactCoreService)
        self.analytics = ServiceRegistry.get(ContactAnalyticsService)

    # Core CRUD operations - delegate to core service
    def get_by_id(self, contact_id):
        """Get a contact by ID."""
        return self.core.get_by_id(contact_id)

    def get_all(self):
        """Get all contacts."""
        return self.core.get_all()

    def create(self, data):
        """Create a new contact."""
        return self.core.create(data)

    def update(self, contact_id_or_obj, data):
        """Update a contact."""
        return self.core.update(contact_id_or_obj, data)

    def delete(self, contact_id):
        """Delete a contact."""
        return self.core.delete(contact_id)

    def get_filtered_contacts(self, has_opportunities=None, has_company=None, skill_level=None):
        """Get contacts based on filter criteria."""
        return self.core.get_filtered_contacts(has_opportunities, has_company, skill_level)

    # Analytics operations - delegate to analytics service
    def get_stats(self):
        """Get general contact statistics."""
        return self.analytics.get_stats()

    def get_top_contacts(self, limit=5):
        """Get top contacts by opportunity count."""
        return self.analytics.get_top_contacts(limit)

    def get_skill_segments(self):
        """Get contact segments by skill level."""
        return self.analytics.get_skill_segments()

    def prepare_growth_data(self):
        """Prepare growth data for the chart."""
        return self.analytics.prepare_growth_data()

    def get_skill_distribution(self):
        """Get distribution of contacts by skill level."""
        return self.analytics.get_skill_distribution()

    def get_skill_area_distribution(self):
        """Get distribution of contacts by skill area."""
        return self.analytics.get_skill_area_distribution()
