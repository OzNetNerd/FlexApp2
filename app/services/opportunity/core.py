# app/services/opportunity/core.py
from datetime import datetime, timedelta
from app.services.service_base import BaseFeatureService
from app.models import Opportunity


class OpportunityService(BaseFeatureService):
    def __init__(self):
        super().__init__(Opportunity)

    def get_dashboard_statistics(self):
        """Get opportunity dashboard statistics."""
        stats = super().get_dashboard_statistics()
        stats.update({
            "active_count": Opportunity.query.filter_by(status="active").count(),
            "total_value": self.calculate_total_value(),
            "win_rate": self.calculate_win_rate()
        })
        return stats

    def calculate_total_value(self):
        """Calculate total value of active opportunities."""
        from app.models.base import db
        from sqlalchemy import func
        return db.session.query(func.sum(Opportunity.value)).filter_by(status="active").scalar() or 0

    def calculate_win_rate(self):
        """Calculate the win rate of opportunities."""
        from app.models.base import db
        total = Opportunity.query.filter(Opportunity.status.in_(["won", "lost"])).count()
        if total == 0:
            return 0
        won = Opportunity.query.filter_by(status="won").count()
        return round((won / total) * 100)

    def get_filtered_opportunities(self, status=None, stage=None, priority=None):
        """Get filtered opportunities based on criteria."""
        query = Opportunity.query

        if status:
            query = query.filter_by(status=status)

        if stage:
            query = query.filter_by(stage=stage)

        if priority:
            query = query.filter_by(priority=priority)

        return query.order_by(Opportunity.close_date.asc()).all()

    def get_hot_opportunities(self, limit=5):
        """Get hot opportunities with high priority."""
        return (
            Opportunity.query.filter_by(status="active", priority="high")
            .order_by(Opportunity.close_date.asc())
            .limit(limit)
            .all()
        )

    def get_statistics(self):
        """Get opportunity statistics."""
        return {
            "total": Opportunity.query.count(),
            "active": Opportunity.query.filter_by(status="active").count(),
            "won": Opportunity.query.filter_by(status="won").count(),
            "lost": Opportunity.query.filter_by(status="lost").count(),
            "closing_soon": Opportunity.query.filter(
                Opportunity.status == "active",
                Opportunity.close_date <= (datetime.now() + timedelta(days=30))
            ).count()
        }