from flask import render_template, request
from flask_login import login_required
from app.models.pages.company import Company
from app.routes.web.utils.context import TableContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.pages.companies import companies_bp

@companies_bp.route("/view2", methods=["GET"])
@login_required
def view2():
    return render_template(
        "pages/companies/view.html",
        id=0,
        model_name="Company",
        entity_name="Demo Company",
        read_only=True,
        submit_url="#",
        csrf_input=""
    )

@companies_bp.route("/records", methods=["GET"])
@login_required
def records():
    # Create appropriate context for the records view
    context = TableContext(
        model_class=Company,
        read_only=True,
        action="view",
        show_heading=True
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/companies/records.html",
        context=context,
        error_message="An error occurred while rendering the companies records page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)