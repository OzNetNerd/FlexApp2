# app/routes/api/clients/contacts.py

from app.routes.api.clients import ApiClient


class ContactApiClient(ApiClient):
    """Client for interacting with the Contact API."""

    def __init__(self):
        super().__init__('/api/contacts')

    # CRUD operations
    def get_all(self):
        """Get all contacts."""
        return self.get(f"{self.base_path}")

    def get_by_id(self, contact_id):
        """Get a contact by ID."""
        return self.get(f"{self.base_path}/{contact_id}")

    def create(self, data):
        """Create a new contact."""
        return self.post(f"{self.base_path}", data)

    def update(self, contact_id, data):
        """Update a contact."""
        return self.put(f"{self.base_path}/{contact_id}", data)

    def delete_contact(self, contact_id):
        """Delete a contact."""
        return self.delete(f"{self.base_path}/{contact_id}")

    # Dashboard operations
    def get_dashboard_stats(self):
        """Get statistics for the contacts dashboard."""
        return self.get(f"{self.base_path}/dashboard/stats")

    def get_top_contacts(self, limit=5):
        """Get top contacts by opportunity count."""
        return self.get(f"{self.base_path}/dashboard/top", params={"limit": limit})

    def get_engagement_segments(self):
        """Get contact segments by engagement level."""
        return self.get(f"{self.base_path}/dashboard/segments")

    def get_growth_data(self, months_back=6):
        """Get growth data for the chart."""
        return self.get(f"{self.base_path}/dashboard/growth", params={"months_back": months_back})

    # Statistics operations
    def get_statistics(self):
        """Get comprehensive statistics for the statistics page."""
        return self.get(f"{self.base_path}/statistics")

    # Filter operations
    def get_filtered_contacts(self, filters):
        """Get contacts based on filter criteria."""
        return self.get(f"{self.base_path}/filtered", params=filters)