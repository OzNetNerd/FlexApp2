from flask import render_template, request
from flask_login import login_required
from datetime import datetime
import random
from app.models.pages.contact import Contact
from app.models.pages.company import Company
from app.routes.web.utils.blueprint_factory import create_crud_blueprint, BlueprintConfig
from app.models.base import db

# Create the blueprint with the Contact model
contacts_bp = create_crud_blueprint(BlueprintConfig(model_class=Contact))


@contacts_bp.route("/", methods=["GET"])
@login_required
def contacts_dashboard():
    # Get basic statistics
    total_contacts = Contact.query.count()

    # Get top contacts (those associated with most opportunities)
    # Use the opportunity_relationships for joining instead of the property
    top_contacts = (
        db.session.query(Contact, db.func.count(Contact.opportunity_relationships).label("opportunity_count"))
        .outerjoin(Contact.opportunity_relationships)
        .group_by(Contact.id)
        .order_by(db.func.count(Contact.opportunity_relationships).desc())
        .limit(5)
        .all()
    )

    # Calculate simple statistics
    stats = {
        "total_contacts": total_contacts,
        "with_opportunities": db.session.query(Contact).filter(Contact.opportunity_relationships.any()).distinct().count(),
        "with_skills": db.session.query(Contact).filter(Contact.skill_level.isnot(None)).count(),
        "with_companies": db.session.query(Contact).filter(Contact.company_id.isnot(None)).count(),
    }

    # Get contacts by skill level
    skill_segments = [
        {
            "name": "Expert",
            "count": db.session.query(Contact).filter(Contact.skill_level == "Expert").count(),
            "percentage": calculate_percentage(db.session.query(Contact).filter(Contact.skill_level == "Expert").count(), total_contacts),
        },
        {
            "name": "Advanced",
            "count": db.session.query(Contact).filter(Contact.skill_level == "Advanced").count(),
            "percentage": calculate_percentage(db.session.query(Contact).filter(Contact.skill_level == "Advanced").count(), total_contacts),
        },
        {
            "name": "Intermediate",
            "count": db.session.query(Contact).filter(Contact.skill_level == "Intermediate").count(),
            "percentage": calculate_percentage(
                db.session.query(Contact).filter(Contact.skill_level == "Intermediate").count(), total_contacts
            ),
        },
        {
            "name": "Beginner",
            "count": db.session.query(Contact).filter(Contact.skill_level == "Beginner").count(),
            "percentage": calculate_percentage(db.session.query(Contact).filter(Contact.skill_level == "Beginner").count(), total_contacts),
        },
    ]

    # Sample data for growth chart
    growth_data = prepare_growth_data()

    return render_template(
        "pages/contacts/dashboard.html", stats=stats, skill_segments=skill_segments, top_contacts=top_contacts, growth_data=growth_data
    )


# Helper functions
def calculate_percentage(count, total):
    if total == 0:
        return 0
    return round((count / total) * 100)


def prepare_growth_data():
    # Generate sample growth data for the chart
    months = []
    new_contacts = []
    total_contacts = []

    current_month = datetime.now().month
    current_year = datetime.now().year

    for i in range(6):
        month = (current_month - i) % 12
        if month == 0:
            month = 12
        year = current_year - ((current_month - i) // 12)

        # Month name for label
        month_name = datetime(year, month, 1).strftime("%b %Y")
        months.append(month_name)

        # Sample data - in a real app, these would be calculated from the database
        new_contacts.append(random.randint(5, 20))
        total_contacts.append(random.randint(50, 150))

    # Reverse lists to display chronologically
    months.reverse()
    new_contacts.reverse()
    total_contacts.reverse()

    return {"labels": months, "new_contacts": new_contacts, "total_contacts": total_contacts}


@contacts_bp.route("/filtered", methods=["GET"])
@login_required
def filtered_contacts():
    # Start with base query
    query = Contact.query

    # Get contacts with opportunities
    has_opportunities = request.args.get("has_opportunities")
    if has_opportunities == "yes":
        query = query.filter(Contact.opportunity_relationships.any())
    elif has_opportunities == "no":
        query = query.filter(~Contact.opportunity_relationships.any())

    # Get contacts with companies
    has_company = request.args.get("has_company")
    if has_company == "yes":
        query = query.filter(Contact.company_id.isnot(None))
    elif has_company == "no":
        query = query.filter(Contact.company_id.is_(None))

    # Get contacts by skill level
    skill_level = request.args.get("skill_level")
    if skill_level and skill_level != "all":
        query = query.filter(Contact.skill_level == skill_level)

    # Get contacts
    contacts = query.order_by(Contact.last_name.asc(), Contact.first_name.asc()).all()

    # Get all companies for the dropdown
    companies = Company.query.order_by(Company.name.asc()).all()

    return render_template(
        "pages/contacts/filtered.html",
        contacts=contacts,
        companies=companies,
        filters={"has_opportunities": has_opportunities, "has_company": has_company, "skill_level": skill_level},
    )


@contacts_bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    # Total contacts
    total_contacts = Contact.query.count()

    # Contacts with opportunities - use opportunity_relationships instead of the property
    with_opportunities = db.session.query(Contact).filter(Contact.opportunity_relationships.any()).distinct().count()

    # Contacts with skills
    with_skills = db.session.query(Contact).filter(Contact.skill_level.isnot(None)).count()

    # Contacts without company
    without_company = db.session.query(Contact).filter(Contact.company_id.is_(None)).count()

    # Get skill distribution
    skill_distribution = db.session.query(Contact.skill_level, db.func.count(Contact.id).label("count")).group_by(Contact.skill_level).all()

    # Get primary skill area distribution
    skill_area_distribution = (
        db.session.query(Contact.primary_skill_area, db.func.count(Contact.id).label("count"))
        .filter(Contact.primary_skill_area.isnot(None))
        .group_by(Contact.primary_skill_area)
        .all()
    )

    return render_template(
        "pages/contacts/statistics.html",
        total_contacts=total_contacts,
        with_opportunities=with_opportunities,
        with_skills=with_skills,
        without_company=without_company,
        skill_distribution=skill_distribution,
        skill_area_distribution=skill_area_distribution,
    )
