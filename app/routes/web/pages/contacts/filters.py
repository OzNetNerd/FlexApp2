from flask import render_template, request
from flask_login import login_required
from app.models.pages.company import Company
from app.services.contact_service import ContactService
from . import contacts_bp

contact_service = ContactService()


@contacts_bp.route("/filtered", methods=["GET"])
@login_required
def filtered_contacts():
    has_opportunities = request.args.get("has_opportunities")
    has_company = request.args.get("has_company")
    skill_level = request.args.get("skill_level")

    contacts = contact_service.get_filtered_contacts(
        has_opportunities=has_opportunities,
        has_company=has_company,
        skill_level=skill_level
    )

    companies = Company.query.order_by(Company.name.asc()).all()

    return render_template(
        "pages/contacts/filtered.html",
        contacts=contacts,
        companies=companies,
        filters={"has_opportunities": has_opportunities, "has_company": has_company, "skill_level": skill_level},
    )