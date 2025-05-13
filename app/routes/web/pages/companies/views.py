# app/routes/web/pages/companies/views.py

from flask import request
from flask_login import login_required
from app.models.pages.company import Company
from app.routes.web.utils.context import TableContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.pages.companies import companies_bp
import json
from datetime import datetime


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@companies_bp.route("/records", methods=["GET"])
@login_required
def records():
    from app.services.company import CompanyService

    # Get data from service
    company_service = CompanyService()
    companies = company_service.get_filtered_companies(request.args.to_dict())

    # Convert to dict format for table
    table_data = [company.to_dict() for company in companies]

    # Properly serialize to JSON with datetime handling
    json_data = json.dumps(table_data, default=json_serial)

    # Create appropriate context for the records view
    context = TableContext(
        model_class=Company,
        read_only=True,
        action="view",
        show_heading=True,
        table_data=json_data,  # Now sending pre-serialized JSON string
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/companies/records.html",
        context=context,
        error_message="An error occurred while rendering the companies records page",
        endpoint_name=request.endpoint,
    )

    # Return the safely rendered template
    return render_safely(config)
