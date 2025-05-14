# app/services/opportunity/analytics.py
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from app.models import Opportunity
from app.models.base import db
from app.services.service_base import ServiceBase


class OpportunityAnalyticsService(ServiceBase):
    """Service for opportunity analytics and statistics."""

    def __init__(self):
        """Initialize the Opportunity analytics service."""
        super().__init__()

    def get_total_opportunities(self):
        """Get the total number of opportunities."""
        return Opportunity.query.count()

    def get_dashboard_statistics(self):
        """Get statistics for the opportunities dashboard."""
        return {
            "active_count": Opportunity.query.filter_by(status="active").count(),
            "total_value": db.session.query(func.sum(Opportunity.value)).filter_by(status="active").scalar() or 0,
            "deal_count": Opportunity.query.filter_by(status="active").count(),
            "win_rate": self.calculate_win_rate(),
            "avg_deal_size": self.calculate_avg_deal_size(),
            "closing_soon": Opportunity.query.filter(
                Opportunity.status == "active", Opportunity.close_date <= (datetime.now() + timedelta(days=30))
            ).count(),
            "won_this_month": Opportunity.query.filter(
                Opportunity.status == "won",
                extract("month", Opportunity.close_date) == datetime.now().month,
                extract("year", Opportunity.close_date) == datetime.now().year,
            ).count(),
            "win_rate_change": self.calculate_win_rate_change(),
            "stale_count": self.calculate_stale_opportunities(),
            "hot_opportunities_count": Opportunity.query.filter_by(priority="high").count(),
        }

    def get_pipeline_stages(self):
        """Get data for pipeline stages visualization."""
        return [
            {
                "name": "Qualification",
                "count": Opportunity.query.filter_by(stage="qualification", status="active").count(),
                "value": db.session.query(func.sum(Opportunity.value)).filter_by(stage="qualification",
                                                                                 status="active").scalar() or 0,
                "percentage": self.calculate_stage_percentage("qualification"),
            },
            {
                "name": "Negotiation",
                "count": Opportunity.query.filter_by(stage="negotiation", status="active").count(),
                "value": db.session.query(func.sum(Opportunity.value)).filter_by(stage="negotiation",
                                                                                 status="active").scalar() or 0,
                "percentage": self.calculate_stage_percentage("negotiation"),
            },
            {
                "name": "Closing",
                "count": Opportunity.query.filter_by(stage="closing", status="active").count(),
                "value": db.session.query(func.sum(Opportunity.value)).filter_by(stage="closing",
                                                                                 status="active").scalar() or 0,
                "percentage": self.calculate_stage_percentage("closing"),
            },
        ]

    def get_statistics(self):
        """Get comprehensive statistics for the statistics page."""
        return {
            "total": Opportunity.query.count(),
            "active": Opportunity.query.filter_by(status="active").count(),
            "won": Opportunity.query.filter_by(status="won").count(),
            "lost": Opportunity.query.filter_by(status="lost").count(),
            "total_value": db.session.query(func.sum(Opportunity.value)).filter_by(status="active").scalar() or 0,
            "avg_deal_size": self.calculate_avg_deal_size(),
            "win_rate": self.calculate_win_rate(),
            "stale_count": self.calculate_stale_opportunities()
        }

    def get_pipeline_by_stage(self):
        """Calculate pipeline value by stage."""
        return (
            db.session.query(Opportunity.stage, func.count().label("count"), func.sum(Opportunity.value).label("value"))
            .filter_by(status="active")
            .group_by(Opportunity.stage)
            .all()
        )

    def get_monthly_data(self):
        """Get monthly data for the past 12 months."""
        monthly_data = []
        current_month = datetime.now().month
        current_year = datetime.now().year

        for i in range(12):
            month = (current_month - i) % 12
            if month == 0:
                month = 12
            year = current_year - ((current_month - i) // 12)

            month_name = datetime(year, month, 1).strftime("%b %Y")

            won_count = Opportunity.query.filter(
                Opportunity.status == "won",
                extract("month", Opportunity.close_date) == month,
                extract("year", Opportunity.close_date) == year,
            ).count()

            won_value = (
                    db.session.query(func.sum(Opportunity.value))
                    .filter(
                        Opportunity.status == "won",
                        extract("month", Opportunity.close_date) == month,
                        extract("year", Opportunity.close_date) == year,
                    )
                    .scalar()
                    or 0
            )

            monthly_data.append({"month": month_name, "won_count": won_count, "won_value": won_value})

        monthly_data.reverse()
        return monthly_data

    def calculate_win_rate(self):
        """Calculate the win rate of opportunities."""
        total = Opportunity.query.filter(Opportunity.status.in_(["won", "lost"])).count()
        if total == 0:
            return 0
        won = Opportunity.query.filter_by(status="won").count()
        return round((won / total) * 100)

    def calculate_avg_deal_size(self):
        """Calculate the average deal size of won opportunities."""
        result = db.session.query(func.avg(Opportunity.value)).filter_by(status="won").scalar()
        return result or 0

    def calculate_win_rate_change(self):
        """Calculate win rate change compared to previous period."""
        return 5  # Placeholder value

    def calculate_stale_opportunities(self):
        """Calculate the number of stale opportunities."""
        two_weeks_ago = datetime.now() - timedelta(days=14)
        return Opportunity.query.filter(Opportunity.status == "active",
                                        Opportunity.last_activity_date <= two_weeks_ago).count()

    def calculate_stage_percentage(self, stage):
        """Calculate the percentage of opportunities in a given stage."""
        total_count = Opportunity.query.filter_by(status="active").count()
        if total_count == 0:
            return 0
        stage_count = Opportunity.query.filter_by(stage=stage, status="active").count()
        return round((stage_count / total_count) * 100)

    def _calculate_percentage(self, count, total):
        """Calculate percentage with safety check for division by zero."""
        if total == 0:
            return 0
        return round((count / total) * 100)