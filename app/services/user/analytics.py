# app/services/user/analytics.py
from datetime import datetime, timedelta
import random
from sqlalchemy import func, extract
from app.models.pages.opportunity import Opportunity
from app.services.service_base import ServiceBase
from app.models.base import db


class UserAnalyticsService(ServiceBase):
    """Service for user analytics and statistics."""

    def __init__(self):
        """Initialize the User analytics service."""
        super().__init__()

    def get_dashboard_statistics(self):
        """Get statistics for the dashboard."""

        from app.models.pages.user import User
        from app.models.pages.note import Note

        return {
            "total_users": User.query.count(),
            "admin_count": User.query.filter_by(is_admin=True).count(),
            "regular_count": User.query.filter_by(is_admin=False).count(),
            "new_users_month": User.query.filter(User.created_at >= (datetime.now() - timedelta(days=30))).count(),
            "avg_notes": self.calculate_avg_notes_per_user(),
            "active_users": self.calculate_active_users(),
            "top_user": self.get_top_user_name(),
            "activity_increase": self.calculate_activity_increase(),
            "inactive_count": self.calculate_inactive_users(),
        }

    def get_top_users(self, limit=5):
        """Get top users based on activity."""
        users_with_counts = (
            db.session.query(User, func.count(Note.id).label("notes_count"))
            .outerjoin(User.notes)
            .group_by(User.id)
            .order_by(func.count(Note.id).desc())
            .limit(limit)
            .all()
        )

        result = []
        for user, notes_count in users_with_counts:
            opportunities_count = db.session.query(func.count(Opportunity.id)).filter(Opportunity.created_by_id == user.id).scalar() or 0

            user_dict = user.__dict__.copy()
            user_dict["notes_count"] = notes_count
            user_dict["opportunities_count"] = opportunities_count
            result.append(user_dict)

        return result

    def get_user_categories(self):
        """Get user categories with statistics."""
        return [
            {
                "count": User.query.filter_by(is_admin=False).count(),
                "activity": db.session.query(func.count(Note.id)).join(User).filter(User.is_admin == False).scalar() or 0,
                "percentage": self.calculate_user_percentage(False),
            },
            {
                "count": User.query.filter_by(is_admin=True).count(),
                "activity": db.session.query(func.count(Note.id)).join(User).filter(User.is_admin == True).scalar() or 0,
                "percentage": self.calculate_user_percentage(True),
            },
            {
                "count": User.query.filter(User.created_at >= (datetime.now() - timedelta(days=30))).count(),
                "activity": db.session.query(func.count(Note.id))
                .join(User)
                .filter(User.created_at >= (datetime.now() - timedelta(days=30)))
                .scalar()
                or 0,
                "percentage": self.calculate_new_user_percentage(),
            },
        ]

    def prepare_activity_data(self):
        """Generate activity data for the chart."""
        labels = []
        notes = []
        opportunities = []
        logins = []

        current_month = datetime.now().month
        current_year = datetime.now().year

        for i in range(6):
            month = (current_month - i) % 12
            if month == 0:
                month = 12
            year = current_year - ((current_month - i) // 12)

            month_name = datetime(year, month, 1).strftime("%b %Y")
            labels.append(month_name)

            notes_count = (
                db.session.query(func.count(Note.id))
                .filter(extract("month", Note.created_at) == month, extract("year", Note.created_at) == year)
                .scalar()
                or 0
            )
            notes.append(notes_count)

            opportunities_count = (
                db.session.query(func.count(Opportunity.id))
                .filter(extract("month", Opportunity.created_at) == month, extract("year", Opportunity.created_at) == year)
                .scalar()
                or 0
            )
            opportunities.append(opportunities_count)

            logins.append(random.randint(20, 100))

        labels.reverse()
        notes.reverse()
        opportunities.reverse()
        logins.reverse()

        return {"labels": labels, "notes": notes, "opportunities": opportunities, "logins": logins}

    def get_statistics(self):
        """Get comprehensive statistics about users."""
        total_users = User.query.count()
        regular_users = User.query.filter_by(is_admin=False).count()
        admin_users = User.query.filter_by(is_admin=True).count()

        two_weeks_ago = datetime.now() - timedelta(days=14)
        active_user_ids = db.session.query(Note.user_id).filter(Note.created_at >= two_weeks_ago).distinct().all()
        active_user_ids = [user_id for (user_id,) in active_user_ids]
        inactive_users = User.query.filter(~User.id.in_(active_user_ids)).count() if active_user_ids else User.query.count()

        total_notes = db.session.query(func.count(Note.id)).scalar() or 0
        total_opportunities = db.session.query(func.count(Opportunity.id)).scalar() or 0
        avg_activity_per_user = (total_notes + total_opportunities) / total_users if total_users > 0 else 0

        user_activity_by_role = []

        admin_notes = db.session.query(func.count(Note.id)).join(User).filter(User.is_admin == True).scalar() or 0
        admin_opportunities = (
            db.session.query(func.count(Opportunity.id))
            .join(User, Opportunity.created_by_id == User.id)
            .filter(User.is_admin == True)
            .scalar()
            or 0
        )

        user_activity_by_role.append({"role": "admin", "count": admin_users, "notes": admin_notes, "opportunities": admin_opportunities})

        regular_notes = db.session.query(func.count(Note.id)).join(User).filter(User.is_admin == False).scalar() or 0
        regular_opportunities = (
            db.session.query(func.count(Opportunity.id))
            .join(User, Opportunity.created_by_id == User.id)
            .filter(User.is_admin == False)
            .scalar()
            or 0
        )

        user_activity_by_role.append(
            {"role": "regular", "count": regular_users, "notes": regular_notes, "opportunities": regular_opportunities}
        )

        monthly_data = []
        current_month = datetime.now().month
        current_year = datetime.now().year

        for i in range(12):
            month = (current_month - i) % 12
            if month == 0:
                month = 12
            year = current_year - ((current_month - i) // 12)

            month_name = datetime(year, month, 1).strftime("%b %Y")

            new_users = User.query.filter(extract("month", User.created_at) == month, extract("year", User.created_at) == year).count()

            notes = (
                db.session.query(func.count(Note.id))
                .filter(extract("month", Note.created_at) == month, extract("year", Note.created_at) == year)
                .scalar()
                or 0
            )

            opportunities = (
                db.session.query(func.count(Opportunity.id))
                .filter(extract("month", Opportunity.created_at) == month, extract("year", Opportunity.created_at) == year)
                .scalar()
                or 0
            )

            monthly_data.append({"month": month_name, "new_users": new_users, "notes": notes, "opportunities": opportunities})

        monthly_data.reverse()

        return {
            "total_users": total_users,
            "regular_users": regular_users,
            "admin_users": admin_users,
            "inactive_users": inactive_users,
            "avg_activity_per_user": avg_activity_per_user,
            "user_activity_by_role": user_activity_by_role,
            "monthly_data": monthly_data,
        }

    # Helper methods
    def calculate_avg_notes_per_user(self):
        """Calculate average notes per user."""
        total_users = User.query.count()
        if total_users == 0:
            return 0
        total_notes = db.session.query(func.count(Note.id)).scalar() or 0
        return round(total_notes / total_users, 1)

    def calculate_active_users(self):
        """Calculate number of active users in the past week."""
        one_week_ago = datetime.now() - timedelta(days=7)
        return db.session.query(func.count(func.distinct(Note.user_id))).filter(Note.created_at >= one_week_ago).scalar() or 0

    def get_top_user_name(self):
        """Get the name of the most active user."""
        result = (
            db.session.query(User.name, func.count(Note.id).label("notes_count"))
            .join(User.notes)
            .group_by(User.id)
            .order_by(func.count(Note.id).desc())
            .first()
        )

        return result.name if result else "N/A"

    def calculate_activity_increase(self):
        """Calculate activity increase."""
        return 8  # Placeholder value

    def calculate_inactive_users(self):
        """Calculate number of inactive users."""
        two_weeks_ago = datetime.now() - timedelta(days=14)
        active_user_ids = db.session.query(Note.user_id).filter(Note.created_at >= two_weeks_ago).distinct().all()
        active_user_ids = [user_id for (user_id,) in active_user_ids]
        return User.query.filter(~User.id.in_(active_user_ids)).count() if active_user_ids else User.query.count()

    def calculate_user_percentage(self, is_admin):
        """Calculate percentage of users by admin status."""
        total_count = User.query.count()
        if total_count == 0:
            return 0
        admin_count = User.query.filter_by(is_admin=is_admin).count()
        return round((admin_count / total_count) * 100)

    def calculate_new_user_percentage(self):
        """Calculate percentage of new users."""
        total_count = User.query.count()
        if total_count == 0:
            return 0
        new_user_count = User.query.filter(User.created_at >= (datetime.now() - timedelta(days=30))).count()
        return round((new_user_count / total_count) * 100)
