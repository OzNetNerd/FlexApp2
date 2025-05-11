from flask import request
from flask_login import login_required
from app.models import Opportunity
from app.routes.web.utils.context import TableContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.pages.opportunities import opportunities_bp

@opportunities_bp.route("/records", methods=["GET"])
@login_required
def records():
    # Create appropriate context for the records view
    context = TableContext(
        model_class=Opportunity,
        read_only=True,
        action="view",
        show_heading=True
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/opportunities/records.html",
        context=context,
        error_message="An error occurred while rendering the opportunities records page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)