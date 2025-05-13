# app/services/opportunity/__init__.py
from app.services.service_base import ServiceBase, ServiceRegistry
from app.services.opportunity.core import OpportunityCoreService
from app.services.opportunity.analytics import OpportunityAnalyticsService
from app.services.opportunity.forecast import OpportunityForecastService


class OpportunityService(ServiceBase):
    """Main service for managing opportunities."""

    def __init__(self):
        """Initialize the Opportunity service with sub-services."""
        super().__init__()
        self.core = ServiceRegistry.get(OpportunityCoreService)
        self.analytics = ServiceRegistry.get(OpportunityAnalyticsService)
        self.forecast = ServiceRegistry.get(OpportunityForecastService)

    # Core operations
    def get_by_id(self, opportunity_id):
        """Get an opportunity by ID."""
        return self.core.get_by_id(opportunity_id)

    def get_all(self):
        """Get all opportunities."""
        return self.core.get_all()

    def get_filtered_opportunities(self, status=None, stage=None, priority=None):
        """Get filtered opportunities based on criteria."""
        return self.core.get_filtered_opportunities(status, stage, priority)

    def get_hot_opportunities(self, limit=5):
        """Get hot opportunities with high priority."""
        return self.core.get_hot_opportunities(limit)

    # Analytics operations
    def get_dashboard_statistics(self):
        """Get statistics for the opportunities dashboard."""
        return self.analytics.get_dashboard_statistics()

    def get_pipeline_stages(self):
        """Get data for pipeline stages visualization."""
        return self.analytics.get_pipeline_stages()

    def get_overall_statistics(self):
        """Get high-level statistics about opportunities."""
        return self.analytics.get_overall_statistics()

    def get_pipeline_by_stage(self):
        """Calculate pipeline value by stage."""
        return self.analytics.get_pipeline_by_stage()

    def get_monthly_data(self):
        """Get monthly data for the past 12 months."""
        return self.analytics.get_monthly_data()

    def calculate_win_rate(self):
        """Calculate the win rate of opportunities."""
        return self.analytics.calculate_win_rate()

    def calculate_avg_deal_size(self):
        """Calculate the average deal size of won opportunities."""
        return self.analytics.calculate_avg_deal_size()

    def calculate_win_rate_change(self):
        """Calculate win rate change compared to previous period."""
        return self.analytics.calculate_win_rate_change()

    def calculate_stale_opportunities(self):
        """Calculate the number of stale opportunities."""
        return self.analytics.calculate_stale_opportunities()

    def calculate_stage_percentage(self, stage):
        """Calculate the percentage of opportunities in a given stage."""
        return self.analytics.calculate_stage_percentage(stage)

    # Forecast operations
    def prepare_forecast_data(self):
        """Generate forecast data for the next 6 months."""
        return self.forecast.prepare_forecast_data()
