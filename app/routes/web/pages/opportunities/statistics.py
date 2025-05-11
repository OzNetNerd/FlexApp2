from flask import request
from flask_login import login_required
from app.services.opportunity_service import OpportunityService
from . import opportunities_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

opportunity_service = OpportunityService()

@opportunities_bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    overall_stats = opportunity_service.get_overall_statistics()
    pipeline_by_stage = opportunity_service.get_pipeline_by_stage()
    monthly_data = opportunity_service.get_monthly_data()

    # Create context for the statistics view
    context = WebContext(
        title="Opportunity Statistics",
        read_only=True,
        total_opportunities=overall_stats["total"],
        active_opportunities=overall_stats["active"],
        won_opportunities=overall_stats["won"],
        lost_opportunities=overall_stats["lost"],
        pipeline_by_stage=pipeline_by_stage,
        monthly_data=monthly_data,
        currency_symbol="$"
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/opportunities/statistics.html",
        context=context,
        error_message="An error occurred while rendering the opportunity statistics page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)