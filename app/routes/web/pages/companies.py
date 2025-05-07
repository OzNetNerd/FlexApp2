from flask import render_template, request
from flask_login import login_required
from datetime import datetime
import random
from app.models.pages.company import Company
from app.routes.web.utils.blueprint_factory import create_crud_blueprint, BlueprintConfig
from app.models.base import db

# Create the blueprint with the Company model
companies_bp = create_crud_blueprint(BlueprintConfig(model_class=Company))


@companies_bp.route("/", methods=["GET"], endpoint="index")
@login_required
def companies_dashboard():
    # Get basic statistics
    total_companies = Company.query.count()

    # Get top companies (those with most opportunities)
    top_companies = (
        db.session.query(Company, db.func.count(Company.opportunities).label("opportunity_count"))
        .outerjoin(Company.opportunities)
        .group_by(Company.id)
        .order_by(db.func.count(Company.opportunities).desc())
        .limit(5)
        .all()
    )

    # Removed the problematic notes handling section
    # Notes display will be handled in the template

    # Calculate simple statistics
    stats = {
        "total_companies": total_companies,
        "with_opportunities": db.session.query(Company).filter(Company.opportunities.any()).count(),
        "with_contacts": db.session.query(Company).filter(Company.contacts.any()).count(),
        "with_capabilities": db.session.query(Company).filter(Company.company_capabilities.any()).count(),
    }

    # Get companies by number of opportunities
    segments = [
        {
            "name": "High Engagement",
            "count": db.session.query(Company)
            .join(Company.opportunities)
            .group_by(Company.id)
            .having(db.func.count(Company.opportunities) > 2)
            .count(),
            "percentage": calculate_percentage(
                db.session.query(Company)
                .join(Company.opportunities)
                .group_by(Company.id)
                .having(db.func.count(Company.opportunities) > 2)
                .count(),
                total_companies,
            ),
        },
        {
            "name": "Medium Engagement",
            "count": db.session.query(Company)
            .join(Company.opportunities)
            .group_by(Company.id)
            .having(db.func.count(Company.opportunities).between(1, 2))
            .count(),
            "percentage": calculate_percentage(
                db.session.query(Company)
                .join(Company.opportunities)
                .group_by(Company.id)
                .having(db.func.count(Company.opportunities).between(1, 2))
                .count(),
                total_companies,
            ),
        },
        {
            "name": "No Opportunities",
            "count": db.session.query(Company)
            .outerjoin(Company.opportunities)
            .group_by(Company.id)
            .having(db.func.count(Company.opportunities) == 0)
            .count(),
            "percentage": calculate_percentage(
                db.session.query(Company)
                .outerjoin(Company.opportunities)
                .group_by(Company.id)
                .having(db.func.count(Company.opportunities) == 0)
                .count(),
                total_companies,
            ),
        },
    ]

    # Sample data for growth chart
    growth_data = prepare_growth_data()

    return render_template(
        "pages/companies/dashboard.html", stats=stats, segments=segments, top_companies=top_companies, growth_data=growth_data
    )


# Helper functions
def calculate_percentage(count, total):
    if total == 0:
        return 0
    return round((count / total) * 100)


def prepare_growth_data():
    # Generate sample growth data for the chart
    months = []
    new_companies = []
    total_companies = []

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
        new_companies.append(random.randint(5, 20))
        total_companies.append(random.randint(50, 150))

    # Reverse lists to display chronologically
    months.reverse()
    new_companies.reverse()
    total_companies.reverse()

    return {"labels": months, "new_companies": new_companies, "total_companies": total_companies}


@companies_bp.route("/filtered", methods=["GET"])
@login_required
def filtered_companies():
    # Start with base query
    query = Company.query

    # Get companies with opportunities
    has_opportunities = request.args.get("has_opportunities")
    if has_opportunities == "yes":
        query = query.filter(Company.opportunities.any())
    elif has_opportunities == "no":
        query = query.filter(~Company.opportunities.any())

    # Get companies with contacts
    has_contacts = request.args.get("has_contacts")
    if has_contacts == "yes":
        query = query.filter(Company.contacts.any())
    elif has_contacts == "no":
        query = query.filter(~Company.contacts.any())

    # Get companies with capabilities
    has_capabilities = request.args.get("has_capabilities")
    if has_capabilities == "yes":
        query = query.filter(Company.company_capabilities.any())
    elif has_capabilities == "no":
        query = query.filter(~Company.company_capabilities.any())

    # Get companies
    companies = query.order_by(Company.name.asc()).all()

    return render_template(
        "pages/companies/filtered.html",
        companies=companies,
        filters={"has_opportunities": has_opportunities, "has_contacts": has_contacts, "has_capabilities": has_capabilities},
    )


@companies_bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    # Total companies
    total_companies = Company.query.count()

    # Companies with opportunities
    with_opportunities = db.session.query(Company).filter(Company.opportunities.any()).count()

    # Companies with contacts
    with_contacts = db.session.query(Company).filter(Company.contacts.any()).count()

    # Companies with no engagement
    no_engagement = (
        db.session.query(Company)
        .outerjoin(Company.opportunities)
        .outerjoin(Company.contacts)
        .group_by(Company.id)
        .having(db.func.count(Company.opportunities) == 0, db.func.count(Company.contacts) == 0)
        .count()
    )

    return render_template(
        "pages/companies/statistics.html",
        total_companies=total_companies,
        with_opportunities=with_opportunities,
        with_contacts=with_contacts,
        no_engagement=no_engagement,
    )


@companies_bp.route("/view2", methods=["GET"])
@login_required
def view2():
    return render_template(
        "pages/companies/view.html",
        id=0,  # Add id parameter
        model_name="Company",  # These parameters are likely needed too
        entity_name="Demo Company",
        read_only=True,
        submit_url="#",  # For the form action
        csrf_input=""  # For CSRF protection
    )

@companies_bp.route("/index2", methods=["GET"])
@login_required
def index2():
    return render_template(
        "pages/companies/index.html",
        id=0,  # Add id parameter
        model_name="Company",  # These parameters are likely needed too
        entity_name="Demo Company",
        read_only=True,
        submit_url="#",  # For the form action
        csrf_input="",
        entity_base_route="",
        api_url = '/api/companies',
    )