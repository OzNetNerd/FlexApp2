# app/services/user/core.py
from app.services.service_base import BaseFeatureService
from app.models.pages.user import User


class UserService(BaseFeatureService):
    def __init__(self):
        super().__init__(User)

    def get_dashboard_statistics(self):
        """Get user dashboard statistics."""
        stats = super().get_dashboard_statistics()
        stats.update({
            "total_users": User.query.count(),
            "admin_count": self.count_admin_users(),
            "regular_count": self.count_regular_users(),
            "new_users_month": self.count_new_users_month()
        })
        return stats

    def count_admin_users(self):
        """Count users with admin privileges."""
        return User.query.filter_by(is_admin=True).count()

    def count_regular_users(self):
        """Count regular users."""
        return User.query.filter_by(is_admin=False).count()

    def count_new_users_month(self):
        """Count new users in the last 30 days."""
        from datetime import datetime, timedelta
        return User.query.filter(User.created_at >= (datetime.now() - timedelta(days=30))).count()

    def get_statistics(self):
        """Get user statistics."""
        return {
            "total_users": User.query.count(),
            "admin_users": self.count_admin_users(),
            "regular_users": self.count_regular_users(),
            "inactive_users": self.count_inactive_users()
        }

    def count_inactive_users(self):
        """Count users with no activity."""
        from datetime import datetime, timedelta
        from app.models.pages.note import Note

        two_weeks_ago = datetime.now() - timedelta(days=14)
        active_user_ids = User.query.join(Note).filter(Note.created_at >= two_weeks_ago).with_entities(
            User.id).distinct().all()
        active_user_ids = [user_id for (user_id,) in active_user_ids]
        return User.query.filter(~User.id.in_(active_user_ids)).count() if active_user_ids else User.query.count()

    def get_filtered_users(self, filters):
        """Get filtered users based on criteria."""
        from datetime import datetime, timedelta
        from app.models.pages.note import Note
        from app.models.base import db

        query = User.query
        is_admin = filters.get("is_admin")
        period = filters.get("period")
        activity = filters.get("activity")

        if is_admin:
            is_admin_bool = is_admin.lower() == "true"
            query = query.filter_by(is_admin=is_admin_bool)

        if period:
            if period == "month":
                query = query.filter(User.created_at >= (datetime.now() - timedelta(days=30)))
            elif period == "quarter":
                query = query.filter(User.created_at >= (datetime.now() - timedelta(days=90)))
            elif period == "year":
                query = query.filter(User.created_at >= (datetime.now() - timedelta(days=365)))

        filtered_users = query.order_by(User.created_at.desc()).all()

        if activity:
            user_notes = {}
            for user in filtered_users:
                note_count = Note.query.filter_by(user_id=user.id).count()
                user_notes[user.id] = note_count

            all_note_counts = sorted(user_notes.values())

            if all_note_counts:
                max_notes = max(all_note_counts)
                high_threshold = max_notes * 0.7
                medium_threshold = max_notes * 0.3

                if activity == "high":
                    filtered_users = [user for user in filtered_users if user_notes.get(user.id, 0) >= high_threshold]
                elif activity == "medium":
                    filtered_users = [user for user in filtered_users if
                                      medium_threshold <= user_notes.get(user.id, 0) < high_threshold]
                elif activity == "low":
                    filtered_users = [user for user in filtered_users if user_notes.get(user.id, 0) < medium_threshold]

        # Attach counts as attributes
        from app.models.pages.opportunity import Opportunity
        for user in filtered_users:
            user.notes_count = Note.query.filter_by(user_id=user.id).count()
            user.opportunities_count = (
                    db.session.query(db.func.count(Opportunity.id))
                    .filter(Opportunity.created_by_id == user.id)
                    .scalar()
                    or 0
            )

        return filtered_users