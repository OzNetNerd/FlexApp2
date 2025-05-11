from flask import request
from flask_login import login_required
from app.services.contact_service import ContactService
from . import contacts_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

contact_service = ContactService()

@contacts_bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    stats = contact_service.get_stats()
    skill_distribution = contact_service.get_skill_distribution()
    skill_area_distribution = contact_service.get_skill_area_distribution()
    without_company = contact_service.get_filtered_contacts(has_company="no")

    # Create context for the statistics view
    context = WebContext(
        title="Contact Statistics",
        read_only=True,
        total_contacts=stats["total_contacts"],
        with_opportunities=stats["with_opportunities"],
        with_skills=stats["with_skills"],
        without_company=len(without_company),
        skill_distribution=skill_distribution,
        skill_area_distribution=skill_area_distribution
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/contacts/statistics.html",
        context=context,
        error_message="An error occurred while rendering the contact statistics page",
        endpoint_name=request.endpoint
    )

    # Return the safely rendered template
    return render_safely(config)