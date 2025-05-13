from flask import request
from flask_login import login_required
from app.services.opportunity import OpportunityService
from . import opportunities_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

opportunity_service = OpportunityService()


@opportunities_bp.route("/filtered", methods=["GET"])
@login_required
def filtered_opportunities():
    status = request.args.get("status")
    stage = request.args.get("stage")
    priority = request.args.get("priority")

    opportunities = opportunity_service.get_filtered_opportunities(status=status, stage=stage, priority=priority)

    # Create context for the filtered view
    context = WebContext(
        title="Filtered Opportunities",
        read_only=True,
        opportunities=opportunities,
        filters={"status": status, "stage": stage, "priority": priority},
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/opportunities/filtered.html",
        context=context,
        error_message="An error occurred while rendering the filtered opportunities page",
        endpoint_name=request.endpoint,
    )

    # Return the safely rendered template
    return render_safely(config)
