# app/services/user/core.py
from datetime import datetime, timedelta
from app.models import User, Note
from app.services.service_base import CRUDService
from app.services.validator_mixin import ValidatorMixin
from app.models.base import db


class UserCoreService(CRUDService, ValidatorMixin):
    """Core service for User CRUD operations."""

    def __init__(self):
        """Initialize the User core service."""
        super().__init__(model_class=User)

    def get_filtered_users(self, filters):
        """Get filtered users based on criteria."""
        query = self.model_class.query
        is_admin = filters.get("is_admin")
        period = filters.get("period")
        activity = filters.get("activity")

        if is_admin:
            is_admin_bool = is_admin.lower() == 'true'
            query = query.filter_by(is_admin=is_admin_bool)

        if period:
            if period == 'month':
                query = query.filter(self.model_class.created_at >= (datetime.now() - timedelta(days=30)))
            elif period == 'quarter':
                query = query.filter(self.model_class.created_at >= (datetime.now() - timedelta(days=90)))
            elif period == 'year':
                query = query.filter(self.model_class.created_at >= (datetime.now() - timedelta(days=365)))

        filtered_users = query.order_by(self.model_class.created_at.desc()).all()

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
            user_dict['opportunities_count'] = db.session.query(db.func.count(self._get_opportunity_model().id)).filter(
                self._get_opportunity_model().created_by_id == user.id
            ).scalar() or 0
            result.append(user_dict)

        return result

    def _get_opportunity_model(self):
        from app.models import Opportunity
        return Opportunity