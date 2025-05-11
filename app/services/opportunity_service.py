from sqlalchemy import func, extract
import random
from app.models import Opportunity
from app.models.base import db
from datetime import datetime, timedelta


class OpportunityService:
    def get_dashboard_statistics(self):
        """Get statistics for the opportunities dashboard"""
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
        """Get data for pipeline stages visualization"""
        return [
            {
                "count": Opportunity.query.filter_by(stage="qualification", status="active").count(),
                "value": db.session.query(func.sum(Opportunity.value)).filter_by(stage="qualification",
                                                                                 status="active").scalar() or 0,
                "percentage": self.calculate_stage_percentage("qualification"),
            },
            {
                "count": Opportunity.query.filter_by(stage="negotiation", status="active").count(),
                "value": db.session.query(func.sum(Opportunity.value)).filter_by(stage="negotiation",
                                                                                 status="active").scalar() or 0,
                "percentage": self.calculate_stage_percentage("negotiation"),
            },
            {
                "count": Opportunity.query.filter_by(stage="closing", status="active").count(),
                "value": db.session.query(func.sum(Opportunity.value)).filter_by(stage="closing",
                                                                                 status="active").scalar() or 0,
                "percentage": self.calculate_stage_percentage("closing"),
            },
        ]

    def get_hot_opportunities(self, limit=5):
        """Get hot opportunities with high priority"""
        return Opportunity.query.filter_by(status="active", priority="high").order_by(
            Opportunity.close_date.asc()).limit(limit).all()

    def prepare_forecast_data(self):
        """Generate forecast data for the next 6 months"""
        months = []
        closed_won = []
        forecast = []
        pipeline = []

        current_month = datetime.now().month
        current_year = datetime.now().year

        for i in range(6):
            month = (current_month + i) % 12
            if month == 0:
                month = 12
            year = current_year + ((current_month + i) // 12)

            # Month name for label
            month_name = datetime(year, month, 1).strftime("%b %Y")
            months.append(month_name)

            # Sample data - in a real app, these would be calculated from the database
            closed_won.append(random.randint(50000, 150000))
            forecast.append(random.randint(100000, 200000))
            pipeline.append(random.randint(200000, 400000))

        return {"labels": months, "closed_won": closed_won, "forecast": forecast, "pipeline": pipeline}

    def get_filtered_opportunities(self, status=None, stage=None, priority=None):
        """Get filtered opportunities based on criteria"""
        query = Opportunity.query

        # Apply filters if provided
        if status:
            query = query.filter_by(status=status)

        if stage:
            query = query.filter_by(stage=stage)

        if priority:
            query = query.filter_by(priority=priority)

        return query.order_by(Opportunity.close_date.asc()).all()

    def get_overall_statistics(self):
        """Get high-level statistics about opportunities"""
        return {
            "total": Opportunity.query.count(),
            "active": Opportunity.query.filter_by(status="active").count(),
            "won": Opportunity.query.filter_by(status="won").count(),
            "lost": Opportunity.query.filter_by(status="lost").count(),
        }

    def get_pipeline_by_stage(self):
        """Calculate pipeline value by stage"""
        return (
            db.session.query(Opportunity.stage, func.count().label("count"), func.sum(Opportunity.value).label("value"))
            .filter_by(status="active")
            .group_by(Opportunity.stage)
            .all()
        )

    def get_monthly_data(self):
        """Get monthly data for the past 12 months"""
        monthly_data = []
        current_month = datetime.now().month
        current_year = datetime.now().year

        for i in range(12):
            month = (current_month - i) % 12
            if month == 0:
                month = 12
            year = current_year - ((current_month - i) // 12)

            # Month name for label
            month_name = datetime(year, month, 1).strftime("%b %Y")

            # Count of won deals for this month
            won_count = Opportunity.query.filter(
                Opportunity.status == "won",
                extract("month", Opportunity.close_date) == month,
                extract("year", Opportunity.close_date) == year
            ).count()

            # Value of won deals for this month
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

        # Reverse the list to get chronological order
        monthly_data.reverse()
        return monthly_data

    # Helper methods moved from opportunities.py
    def calculate_win_rate(self):
        total = Opportunity.query.filter(Opportunity.status.in_(["won", "lost"])).count()
        if total == 0:
            return 0
        won = Opportunity.query.filter_by(status="won").count()
        return round((won / total) * 100)

    def calculate_avg_deal_size(self):
        result = db.session.query(func.avg(Opportunity.value)).filter_by(status="won").scalar()
        return result or 0

    def calculate_win_rate_change(self):
        # Calculate win rate for current quarter vs previous quarter
        # This is a simplified example
        return 5  # Placeholder value

    def calculate_stale_opportunities(self):
        two_weeks_ago = datetime.now() - timedelta(days=14)
        return Opportunity.query.filter(Opportunity.status == "active",
                                        Opportunity.last_activity_date <= two_weeks_ago).count()

    def calculate_stage_percentage(self, stage):
        total_count = Opportunity.query.filter_by(status="active").count()
        if total_count == 0:
            return 0
        stage_count = Opportunity.query.filter_by(stage=stage, status="active").count()
        return round((stage_count / total_count) * 100)