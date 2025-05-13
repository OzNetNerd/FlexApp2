from flask import request
from flask_login import login_required
from app.services.contact import ContactService
from . import contacts_bp
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

contact_service = ContactService()


@contacts_bp.route("/", methods=["GET"])
@login_required
def contacts_dashboard():
    stats = contact_service.get_stats()
    skill_segments = contact_service.get_skill_segments()
    top_contacts = contact_service.get_top_contacts()
    growth_data = contact_service.prepare_growth_data()

    # Create context for the dashboard view
    context = WebContext(
        title="Contacts Dashboard",
        read_only=True,
        stats=stats,
        skill_segments=skill_segments,
        top_contacts=top_contacts,
        growth_data=growth_data,
    )

    # Configure the render_safely call
    config = RenderSafelyConfig(
        template_path="pages/contacts/dashboard.html",
        context=context,
        error_message="An error occurred while rendering the contacts dashboard",
        endpoint_name=request.endpoint,
    )

    # Return the safely rendered template
    return render_safely(config)
