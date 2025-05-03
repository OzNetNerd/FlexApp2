from sqlalchemy import func, extract
import random
from app.models import Opportunity
from flask import render_template
from flask_login import login_required
from datetime import datetime, timedelta
from app.routes.web.blueprint_factory import create_crud_blueprint, BlueprintConfig
from app.models.base import db


opportunities_bp = create_crud_blueprint(BlueprintConfig(model_class=Opportunity))


# Opportunities Dashboard route
@opportunities_bp.route("/", methods=["GET"])
@login_required
def opportunities_dashboard():
    # Get statistics for summary section
    stats = {
        "active_count": Opportunity.query.filter_by(status="active").count(),
        "total_value": db.session.query(func.sum(Opportunity.value)).filter_by(status="active").scalar() or 0,
        "deal_count": Opportunity.query.filter_by(status="active").count(),
        "win_rate": calculate_win_rate(),
        "avg_deal_size": calculate_avg_deal_size(),
        "closing_soon": Opportunity.query.filter(
            Opportunity.status == "active",
            Opportunity.close_date <= (datetime.now() + timedelta(days=30))
        ).count(),
        "won_this_month": Opportunity.query.filter(
            Opportunity.status == "won",
            extract('month', Opportunity.close_date) == datetime.now().month,
            extract('year', Opportunity.close_date) == datetime.now().year
        ).count(),
        "win_rate_change": calculate_win_rate_change(),
        "stale_count": calculate_stale_opportunities(),
        "hot_opportunities_count": Opportunity.query.filter_by(priority="high").count()
    }

    # Get pipeline stages data
    stages = [
        {
            "count": Opportunity.query.filter_by(stage="qualification", status="active").count(),
            "value": db.session.query(func.sum(Opportunity.value)).filter_by(stage="qualification",
                                                                             status="active").scalar() or 0,
            "percentage": calculate_stage_percentage("qualification")
        },
        {
            "count": Opportunity.query.filter_by(stage="negotiation", status="active").count(),
            "value": db.session.query(func.sum(Opportunity.value)).filter_by(stage="negotiation",
                                                                             status="active").scalar() or 0,
            "percentage": calculate_stage_percentage("negotiation")
        },
        {
            "count": Opportunity.query.filter_by(stage="closing", status="active").count(),
            "value": db.session.query(func.sum(Opportunity.value)).filter_by(stage="closing",
                                                                             status="active").scalar() or 0,
            "percentage": calculate_stage_percentage("closing")
        }
    ]

    # Get hot opportunities
    hot_opportunities = Opportunity.query.filter_by(
        status="active",
        priority="high"
    ).order_by(Opportunity.close_date.asc()).limit(5).all()

    # Prepare forecast data for chart
    forecast_data = prepare_forecast_data()

    return render_template(
        "opportunities/dashboard.html",
        stats=stats,
        stages=stages,
        hot_opportunities=hot_opportunities,
        forecast_data=forecast_data,
        currency_symbol="$"
    )


# Helper functions
def calculate_win_rate():
    total = Opportunity.query.filter(Opportunity.status.in_(["won", "lost"])).count()
    if total == 0:
        return 0
    won = Opportunity.query.filter_by(status="won").count()
    return round((won / total) * 100)


def calculate_avg_deal_size():
    result = db.session.query(func.avg(Opportunity.value)).filter_by(status="won").scalar()
    return result or 0


def calculate_win_rate_change():
    # Calculate win rate for current quarter vs previous quarter
    # This is a simplified example
    return 5  # Placeholder value


def calculate_stale_opportunities():
    two_weeks_ago = datetime.now() - timedelta(days=14)
    return Opportunity.query.filter(
        Opportunity.status == "active",
        Opportunity.last_activity_date <= two_weeks_ago
    ).count()


def calculate_stage_percentage(stage):
    total_count = Opportunity.query.filter_by(status="active").count()
    if total_count == 0:
        return 0
    stage_count = Opportunity.query.filter_by(stage=stage, status="active").count()
    return round((stage_count / total_count) * 100)


def prepare_forecast_data():
    # Generate forecast data for the next 6 months
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
        month_name = datetime(year, month, 1).strftime('%b %Y')
        months.append(month_name)

        # Sample data - in a real app, these would be calculated from the database
        closed_won.append(random.randint(50000, 150000))
        forecast.append(random.randint(100000, 200000))
        pipeline.append(random.randint(200000, 400000))

    return {
        "labels": months,
        "closed_won": closed_won,
        "forecast": forecast,
        "pipeline": pipeline
    }