# app/routes/api/clients/pages/users.py

from app.routes.api.clients import ApiClient


class UserApiClient(ApiClient):
    """Client for interacting with the User API."""

    def __init__(self):
        super().__init__("/api/users")

    # CRUD operations
    def get_all(self):
        """Get all users."""
        return self.get(f"{self.base_path}")

    def get_by_id(self, user_id):
        """Get a user by ID."""
        return self.get(f"{self.base_path}/{user_id}")

    def create(self, data):
        """Create a new user."""
        return self.post(f"{self.base_path}", data)

    def update(self, user_id, data):
        """Update a user."""
        return self.put(f"{self.base_path}/{user_id}", data)

    def delete_user(self, user_id):
        """Delete a user."""
        return self.delete(f"{self.base_path}/{user_id}")

    # Dashboard operations
    def get_dashboard_stats(self):
        """Get statistics for the users dashboard."""
        return self.get(f"{self.base_path}/dashboard/stats")

    def get_active_users(self, limit=10):
        """Get active users."""
        return self.get(f"{self.base_path}/dashboard/active", params={"limit": limit})

    def get_recent_users(self, limit=5):
        """Get recently added users."""
        return self.get(f"{self.base_path}/dashboard/recent", params={"limit": limit})

    # Statistics operations
    def get_statistics(self):
        """Get comprehensive statistics for the statistics page."""
        return self.get(f"{self.base_path}/statistics")

    # Filter operations
    def get_filtered_users(self, filters):
        """Get users based on filter criteria."""
        return self.get(f"{self.base_path}/filtered", params=filters)
