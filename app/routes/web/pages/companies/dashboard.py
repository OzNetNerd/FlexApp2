# app/routes/web/pages/companies/dashboard.py

from flask import request
from flask_login import login_required
from app.routes.web.pages.companies import companies_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext


@companies_bp.route("/", methods=["GET"], endpoint="dashboard")
@login_required
def companies_dashboard():
    context = WebContext(title="Companies Dashboard", read_only=True)

    config = RenderSafelyConfig(
        template_path="pages/companies/dashboard.html",
        context=context,
        error_message="An error occurred while rendering the companies dashboard",
        endpoint_name=request.endpoint,
    )

    return render_safely(config)
