# app/services/user_service.py

from sqlalchemy import func, extract
import random
from datetime import datetime, timedelta
from app.models import User, Note, Opportunity
from app.services.crud_service import CRUDService
from app.models.base import db

class UserService(CRUDService):
    def __init__(self, model_class=User):
        super().__init__(model_class)

    def calculate_avg_notes_per_user(self):
        total_users = User.query.count()
        if total_users == 0:
            return 0
        total_notes = db.session.query(func.count(Note.id)).scalar() or 0
        return round(total_notes / total_users, 1)

    def calculate_active_users(self):
        one_week_ago = datetime.now() - timedelta(days=7)
        return db.session.query(func.count(func.distinct(Note.user_id))).filter(
            Note.created_at >= one_week_ago
        ).scalar() or 0

    def get_top_user_name(self):
        result = db.session.query(
            User.name,
            func.count(Note.id).label('notes_count')
        ).join(User.notes).group_by(User.id).order_by(
            func.count(Note.id).desc()
        ).first()

        return result.name if result else "N/A"

    def calculate_activity_increase(self):
        return 8  # Placeholder value

    def calculate_inactive_users(self):
        two_weeks_ago = datetime.now() - timedelta(days=14)
        active_user_ids = db.session.query(Note.user_id).filter(
            Note.created_at >= two_weeks_ago
        ).distinct().all()
        active_user_ids = [user_id for (user_id,) in active_user_ids]
        return User.query.filter(~User.id.in_(active_user_ids)).count() if active_user_ids else User.query.count()

    def calculate_user_percentage(self, is_admin):
        total_count = User.query.count()
        if total_count == 0:
            return 0
        admin_count = User.query.filter_by(is_admin=is_admin).count()
        return round((admin_count / total_count) * 100)

    def calculate_new_user_percentage(self):
        total_count = User.query.count()
        if total_count == 0:
            return 0
        new_user_count = User.query.filter(
            User.created_at >= (datetime.now() - timedelta(days=30))
        ).count()
        return round((new_user_count / total_count) * 100)

    def get_top_users(self, limit=5):
        users_with_counts = db.session.query(
            User,
            func.count(Note.id).label('notes_count')
        ).outerjoin(User.notes).group_by(User.id).order_by(
            func.count(Note.id).desc()
        ).limit(limit).all()

        result = []
        for user, notes_count in users_with_counts:
            opportunities_count = db.session.query(func.count(Opportunity.id)).filter(
                Opportunity.created_by_id == user.id
            ).scalar() or 0

            user_dict = user.__dict__.copy()
            user_dict['notes_count'] = notes_count
            user_dict['opportunities_count'] = opportunities_count
            result.append(user_dict)

        return result

    def prepare_activity_data(self):
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

            notes_count = db.session.query(func.count(Note.id)).filter(
                extract('month', Note.created_at) == month,
                extract('year', Note.created_at) == year
            ).scalar() or 0
            notes.append(notes_count)

            opportunities_count = db.session.query(func.count(Opportunity.id)).filter(
                extract('month', Opportunity.created_at) == month,
                extract('year', Opportunity.created_at) == year
            ).scalar() or 0
            opportunities.append(opportunities_count)

            logins.append(random.randint(20, 100))

        labels.reverse()
        notes.reverse()
        opportunities.reverse()
        logins.reverse()

        return {"labels": labels, "notes": notes, "opportunities": opportunities, "logins": logins}

    def get_dashboard_stats(self):
        return {
            "total_users": User.query.count(),
            "admin_count": User.query.filter_by(is_admin=True).count(),
            "regular_count": User.query.filter_by(is_admin=False).count(),
            "new_users_month": User.query.filter(
                User.created_at >= (datetime.now() - timedelta(days=30))
            ).count(),
            "avg_notes": self.calculate_avg_notes_per_user(),
            "active_users": self.calculate_active_users(),
            "top_user": self.get_top_user_name(),
            "activity_increase": self.calculate_activity_increase(),
            "inactive_count": self.calculate_inactive_users(),
        }

    def get_user_categories(self):
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
                "count": User.query.filter(
                    User.created_at >= (datetime.now() - timedelta(days=30))
                ).count(),
                "activity": db.session.query(func.count(Note.id)).join(User).filter(
                    User.created_at >= (datetime.now() - timedelta(days=30))
                ).scalar() or 0,
                "percentage": self.calculate_new_user_percentage(),
            },
        ]

    def get_filtered_users(self, filters):
        query = User.query
        is_admin = filters.get("is_admin")
        period = filters.get("period")
        activity = filters.get("activity")

        if is_admin:
            is_admin_bool = is_admin.lower() == 'true'
            query = query.filter_by(is_admin=is_admin_bool)

        if period:
            if period == 'month':
                query = query.filter(User.created_at >= (datetime.now() - timedelta(days=30)))
            elif period == 'quarter':
                query = query.filter(User.created_at >= (datetime.now() - timedelta(days=90)))
            elif period == 'year':
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

                if activity == 'high':
                    filtered_users = [user for user in filtered_users if user_notes.get(user.id, 0) >= high_threshold]
                elif activity == 'medium':
                    filtered_users = [user for user in filtered_users
                                    if medium_threshold <= user_notes.get(user.id, 0) < high_threshold]
                elif activity == 'low':
                    filtered_users = [user for user in filtered_users if user_notes.get(user.id, 0) < medium_threshold]

        result = []
        for user in filtered_users:
            user_dict = user.__dict__.copy()
            user_dict['notes_count'] = Note.query.filter_by(user_id=user.id).count()
            user_dict['opportunities_count'] = db.session.query(func.count(Opportunity.id)).filter(
                Opportunity.created_by_id == user.id
            ).scalar() or 0
            result.append(user_dict)

        return result

    def get_statistics(self):
        total_users = User.query.count()
        regular_users = User.query.filter_by(is_admin=False).count()
        admin_users = User.query.filter_by(is_admin=True).count()

        two_weeks_ago = datetime.now() - timedelta(days=14)
        active_user_ids = db.session.query(Note.user_id).filter(
            Note.created_at >= two_weeks_ago
        ).distinct().all()
        active_user_ids = [user_id for (user_id,) in active_user_ids]
        inactive_users = User.query.filter(~User.id.in_(active_user_ids)).count() if active_user_ids else User.query.count()

        total_notes = db.session.query(func.count(Note.id)).scalar() or 0
        total_opportunities = db.session.query(func.count(Opportunity.id)).scalar() or 0
        avg_activity_per_user = (total_notes + total_opportunities) / total_users if total_users > 0 else 0

        user_activity_by_role = []

        admin_notes = db.session.query(func.count(Note.id)).join(User).filter(User.is_admin == True).scalar() or 0
        admin_opportunities = db.session.query(func.count(Opportunity.id)).join(
            User, Opportunity.created_by_id == User.id
        ).filter(User.is_admin == True).scalar() or 0

        user_activity_by_role.append({
            "role": "admin",
            "count": admin_users,
            "notes": admin_notes,
            "opportunities": admin_opportunities
        })

        regular_notes = db.session.query(func.count(Note.id)).join(User).filter(User.is_admin == False).scalar() or 0
        regular_opportunities = db.session.query(func.count(Opportunity.id)).join(
            User, Opportunity.created_by_id == User.id
        ).filter(User.is_admin == False).scalar() or 0

        user_activity_by_role.append({
            "role": "regular",
            "count": regular_users,
            "notes": regular_notes,
            "opportunities": regular_opportunities
        })

        monthly_data = []
        current_month = datetime.now().month
        current_year = datetime.now().year

        for i in range(12):
            month = (current_month - i) % 12
            if month == 0:
                month = 12
            year = current_year - ((current_month - i) // 12)

            month_name = datetime(year, month, 1).strftime("%b %Y")

            new_users = User.query.filter(
                extract('month', User.created_at) == month,
                extract('year', User.created_at) == year
            ).count()

            notes = db.session.query(func.count(Note.id)).filter(
                extract('month', Note.created_at) == month,
                extract('year', Note.created_at) == year
            ).scalar() or 0

            opportunities = db.session.query(func.count(Opportunity.id)).filter(
                extract('month', Opportunity.created_at) == month,
                extract('year', Opportunity.created_at) == year
            ).scalar() or 0

            monthly_data.append({
                "month": month_name,
                "new_users": new_users,
                "notes": notes,
                "opportunities": opportunities
            })

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