# app/services/user/__init__.py
from app.services.service_base import ServiceBase, ServiceRegistry
from app.services.user.core import UserCoreService
from app.services.user.analytics import UserAnalyticsService


class UserService(ServiceBase):
    """Main service for managing users."""

    def __init__(self):
        """Initialize the User service with sub-services."""
        super().__init__()
        self.core = ServiceRegistry.get(UserCoreService)
        self.analytics = ServiceRegistry.get(UserAnalyticsService)

    # Core CRUD methods
    def get_by_id(self, user_id):
        """Get a user by ID."""
        return self.core.get_by_id(user_id)

    def get_all(self):
        """Get all users."""
        return self.core.get_all()

    def create(self, data):
        """Create a new user."""
        return self.core.create(data)

    def update(self, user_id_or_obj, data):
        """Update a user."""
        return self.core.update(user_id_or_obj, data)

    def delete(self, user_id):
        """Delete a user."""
        return self.core.delete(user_id)

    def get_filtered_users(self, filters):
        """Get filtered users based on criteria."""
        return self.core.get_filtered_users(filters)

    # Analytics methods
    def get_dashboard_stats(self):
        """Get statistics for the dashboard."""
        return self.analytics.get_dashboard_stats()

    def get_user_categories(self):
        """Get user categories with statistics."""
        return self.analytics.get_user_categories()

    def prepare_activity_data(self):
        """Generate activity data for the chart."""
        return self.analytics.prepare_activity_data()

    def get_top_users(self, limit=5):
        """Get top users based on activity."""
        return self.analytics.get_top_users(limit)

    def get_statistics(self):
        """Get comprehensive statistics about users."""
        return self.analytics.get_statistics()

    def calculate_avg_notes_per_user(self):
        """Calculate average notes per user."""
        return self.analytics.calculate_avg_notes_per_user()

    def calculate_active_users(self):
        """Calculate number of active users in the past week."""
        return self.analytics.calculate_active_users()

    def get_top_user_name(self):
        """Get the name of the most active user."""
        return self.analytics.get_top_user_name()

    def calculate_activity_increase(self):
        """Calculate activity increase."""
        return self.analytics.calculate_activity_increase()

    def calculate_inactive_users(self):
        """Calculate number of inactive users."""
        return self.analytics.calculate_inactive_users()

    def calculate_user_percentage(self, is_admin):
        """Calculate percentage of users by admin status."""
        return self.analytics.calculate_user_percentage(is_admin)

    def calculate_new_user_percentage(self):
        """Calculate percentage of new users."""
        return self.analytics.calculate_new_user_percentage()