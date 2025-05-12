from flask import request
from flask_login import login_required
from app.services.opportunity import OpportunityService
from . import opportunities_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

opportunity_service = OpportunityService()

@opportunities_bp.route("/", methods=["GET"])
@login_required
def opportunities_dashboard():
    stats = opportunity_service.get_dashboard_statistics()
    stages = opportunity_service.get_pipeline_stages()
    hot_opportunities = opportunity_service.get_hot_opportunities(limit=5)
    forecast_data = opportunity_service.prepare_forecast_data()

    # Create context for the dashboard view
    context = WebContext(
        title="Opportunities Dashboard",
        read_only=True,
        stats=stats,
        stages=stages,
        hot_opportunities=hot_opportunities,
        forecast_data=forecast_data,
        currency_symbol="$"
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/opportunities/dashboard.html",
        context=context,
        error_message="An error occurred while rendering the opportunities dashboard",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)