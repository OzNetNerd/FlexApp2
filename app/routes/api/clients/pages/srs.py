# app/routes/api/clients/srs.py

from app.routes.api.clients import ApiClient


class SRSApiClient(ApiClient):
    """Client for interacting with the SRS API."""

    def __init__(self):
        super().__init__("/api/srs")

    # CRUD operations
    def get_all(self):
        """Get all SRS items."""
        return self.get(f"{self.base_path}")

    def get_by_id(self, item_id):
        """Get an SRS item by ID."""
        return self.get(f"{self.base_path}/{item_id}")

    def create(self, data):
        """Create a new SRS item."""
        return self.post(f"{self.base_path}", data)

    def update(self, item_id, data):
        """Update an SRS item."""
        return self.put(f"{self.base_path}/{item_id}", data)

    def delete_item(self, item_id):
        """Delete an SRS item."""
        return self.delete(f"{self.base_path}/{item_id}")

    # SRS-specific operations
    def get_due_items(self):
        """Get SRS items due for review."""
        return self.get(f"{self.base_path}/due")

    def preview_item_ratings(self, item_id):
        """Preview how long an item would be buried for each rating."""
        return self.get(f"{self.base_path}/{item_id}/preview")

    def review_item(self, item_id, rating):
        """Submit a rating and update the SRS schedule for an item."""
        return self.post(f"{self.base_path}/{item_id}/review", {"rating": rating})

    def get_srs_stats(self):
        """Get current SRS system statistics."""
        return self.get(f"{self.base_path}/stats")

    def create_category(self, data):
        """Create a new SRS category."""
        return self.post(f"{self.base_path}/categories", data)

    def get_categories(self):
        """Get all SRS categories."""
        return self.get(f"{self.base_path}/categories")

    def get_progress_data(self, months=7):
        """Get progress data for charts."""
        return self.get(f"{self.base_path}/progress-data", params={"months": months})

    def update_item_field(self, item_id, data):
        """Update a single field of an SRS item."""
        return self.patch(f"{self.base_path}/{item_id}", data)
