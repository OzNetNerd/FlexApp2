# app/routes/api/clients/companies.py

from app.routes.api.clients import ApiClient


class CompanyApiClient(ApiClient):
    """Client for interacting with the Company API."""

    def __init__(self):
        super().__init__("/api/companies")

    # CRUD operations
    def get_all(self):
        """Get all companies."""
        return self.get(f"{self.base_path}")

    def get_by_id(self, company_id):
        """Get a company by ID."""
        return self.get(f"{self.base_path}/{company_id}")

    def create(self, data):
        """Create a new company."""
        return self.post(f"{self.base_path}", data)

    def update(self, company_id, data):
        """Update a company."""
        return self.put(f"{self.base_path}/{company_id}", data)

    def delete_company(self, company_id):
        """Delete a company."""
        return self.delete(f"{self.base_path}/{company_id}")

    # Dashboard operations
    def get_dashboard_statistics(self):
        """Get statistics for the companies dashboard."""
        return self.get(f"{self.base_path}/dashboard/stats")

    def get_top_companies(self, limit=5):
        """Get top companies by opportunity count."""
        return self.get(f"{self.base_path}/dashboard/top", params={"limit": limit})

    def get_engagement_segments(self):
        """Get company segments by engagement level."""
        return self.get(f"{self.base_path}/dashboard/segments")

    def get_growth_data(self, months_back=6):
        """Get growth data for the chart."""
        return self.get(f"{self.base_path}/dashboard/growth", params={"months_back": months_back})

    # Statistics operations
    def get_statistics(self):
        """Get comprehensive statistics for the statistics page."""
        return self.get(f"{self.base_path}/statistics")

    # Filter operations
    def get_filtered_companies(self, filters):
        """Get companies based on filter criteria."""
        return self.get(f"{self.base_path}/filtered", params=filters)
