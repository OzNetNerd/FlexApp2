# app/services/company/__init__.py
from app.services.service_base import ServiceBase, ServiceRegistry
from app.services.company.core import CompanyCoreService
from app.services.company.analytics import CompanyAnalyticsService


class CompanyService(ServiceBase):
    """Main service for managing companies."""

    def __init__(self):
        """Initialize the Company service with sub-services."""
        super().__init__()
        self.core = ServiceRegistry.get(CompanyCoreService)
        self.analytics = ServiceRegistry.get(CompanyAnalyticsService)

    # Core operations - delegate to core service
    def get_company_by_id(self, company_id):
        """Get a company by ID."""
        return self.core.get_by_id(company_id)

    def get_filtered_companies(self, filters):
        """Get companies based on filter criteria."""
        return self.core.get_filtered_companies(filters)

    # Analytics operations - delegate to analytics service
    def get_total_companies(self):
        """Get the total number of companies."""
        return self.analytics.get_total_companies()

    def get_dashboard_stats(self):
        """Get statistics for the companies dashboard."""
        return self.analytics.get_dashboard_stats()

    def get_top_companies(self, limit=5):
        """Get top companies by opportunity count."""
        return self.analytics.get_top_companies(limit)

    def get_engagement_segments(self):
        """Get company segments by engagement level."""
        return self.analytics.get_engagement_segments()

    def prepare_growth_data(self, months_back=6):
        """Prepare growth data for the chart."""
        return self.analytics.prepare_growth_data(months_back)

    def get_statistics(self):
        """Get comprehensive statistics for the statistics page."""
        return self.analytics.get_statistics()