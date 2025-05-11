from flask import request
from flask_login import login_required
from app.models.pages.contact import Contact
from app.routes.web.utils.context import TableContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from . import contacts_bp

@contacts_bp.route("/records", methods=["GET"])
@login_required
def records():
    # Create appropriate context for the records view
    context = TableContext(
        model_class=Contact,
        read_only=True,
        action="view",
        show_heading=True
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/contacts/records.html",
        context=context,
        error_message="An error occurred while rendering the contacts records page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)