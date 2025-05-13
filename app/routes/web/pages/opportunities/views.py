from flask import request
from flask_login import login_required
from app.models.pages.opportunity import Opportunity
from app.routes.web.utils.context import TableContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.pages.opportunities import opportunities_bp
import json
from datetime import datetime


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@opportunities_bp.route("/records", methods=["GET"])
@login_required
def records():
    from app.services.opportunity import OpportunityService

    # Get data from service
    opportunity_service = OpportunityService()
    opportunities = opportunity_service.get_filtered_opportunities(request.args.to_dict())

    # Convert to dict format for table
    table_data = [opportunity.to_dict() for opportunity in opportunities]

    # Properly serialize to JSON with datetime handling
    json_data = json.dumps(table_data, default=json_serial)

    # Create appropriate context for the records view
    context = TableContext(
        model_class=Opportunity,
        read_only=True,
        action="view",
        show_heading=True,
        table_data=json_data,  # Now sending pre-serialized JSON string
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/opportunities/records.html",
        context=context,
        error_message="An error occurred while rendering the opportunities records page",
        endpoint_name=request.endpoint,
    )

    # Return the safely rendered template
    return render_safely(config)
