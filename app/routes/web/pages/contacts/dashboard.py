from flask import render_template
from flask_login import login_required
from app.services.contact_service import ContactService
from . import contacts_bp

contact_service = ContactService()

@contacts_bp.route("/", methods=["GET"])
@login_required
def contacts_dashboard():
    stats = contact_service.get_stats()
    skill_segments = contact_service.get_skill_segments()
    top_contacts = contact_service.get_top_contacts()
    growth_data = contact_service.prepare_growth_data()

    return render_template(
        "pages/contacts/dashboard.html",
        stats=stats,
        skill_segments=skill_segments,
        top_contacts=top_contacts,
        growth_data=growth_data
    )