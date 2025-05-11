from flask import render_template
from flask_login import login_required
from app.services.contact_service import ContactService
from . import contacts_bp

contact_service = ContactService()

@contacts_bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    stats = contact_service.get_stats()
    skill_distribution = contact_service.get_skill_distribution()
    skill_area_distribution = contact_service.get_skill_area_distribution()
    without_company = contact_service.get_filtered_contacts(has_company="no")

    return render_template(
        "pages/contacts/statistics.html",
        total_contacts=stats["total_contacts"],
        with_opportunities=stats["with_opportunities"],
        with_skills=stats["with_skills"],
        without_company=len(without_company),
        skill_distribution=skill_distribution,
        skill_area_distribution=skill_area_distribution,
    )