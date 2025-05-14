# app/routes/api/clients/pages/opportunities.py

from app.routes.api.clients import ApiClient


class OpportunityApiClient(ApiClient):
    """Client for interacting with the Opportunity API."""

    def __init__(self):
        super().__init__("/api/opportunities")

    # CRUD operations
    def get_all(self):
        """Get all opportunities."""
        return self.get(f"{self.base_path}")

    def get_by_id(self, opportunity_id):
        """Get an opportunity by ID."""
        return self.get(f"{self.base_path}/{opportunity_id}")

    def create(self, data):
        """Create a new opportunity."""
        return self.post(f"{self.base_path}", data)

    def update(self, opportunity_id, data):
        """Update an opportunity."""
        return self.put(f"{self.base_path}/{opportunity_id}", data)

    def delete_opportunity(self, opportunity_id):
        """Delete an opportunity."""
        return self.delete(f"{self.base_path}/{opportunity_id}")

    # Dashboard operations
    def get_dashboard_statistics(self):
        """Get statistics for the opportunities dashboard."""
        return self.get(f"{self.base_path}/dashboard/stats")

    def get_top_opportunities(self, limit=5):
        """Get top opportunities by value."""
        return self.get(f"{self.base_path}/dashboard/top", params={"limit": limit})

    def get_stage_segments(self):
        """Get opportunity segments by stage."""
        return self.get(f"{self.base_path}/dashboard/segments")

    def get_growth_data(self, months_back=6):
        """Get growth data for the chart."""
        return self.get(f"{self.base_path}/dashboard/growth", params={"months_back": months_back})

    # Statistics operations
    def get_statistics(self):
        """Get comprehensive statistics for the statistics page."""
        return self.get(f"{self.base_path}/statistics")

    # Filter operations
    def get_filtered_opportunities(self, filters):
        """Get opportunities based on filter criteria."""
        return self.get(f"{self.base_path}/filtered", params=filters)
