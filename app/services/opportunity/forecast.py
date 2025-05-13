# app/services/opportunity/forecast.py
import random
from datetime import datetime
from app.services.service_base import ServiceBase


class OpportunityForecastService(ServiceBase):
    """Service for opportunity forecasting."""

    def __init__(self):
        """Initialize the Opportunity forecast service."""
        super().__init__()

    def prepare_forecast_data(self):
        """Generate forecast data for the next 6 months."""
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

            month_name = datetime(year, month, 1).strftime("%b %Y")
            months.append(month_name)

            closed_won.append(random.randint(50000, 150000))
            forecast.append(random.randint(100000, 200000))
            pipeline.append(random.randint(200000, 400000))

        return {"labels": months, "closed_won": closed_won, "forecast": forecast, "pipeline": pipeline}
