# app/services/contact/analytics.py
from datetime import datetime
from sqlalchemy import func
from app.models.pages.contact import Contact
from app.models.base import db
from app.services.service_base import ServiceBase


class ContactAnalyticsService(ServiceBase):
    """Service for contact analytics and statistics."""

    def __init__(self):
        """Initialize the Contact analytics service."""
        super().__init__()

    def get_total_contacts(self):
        """Get the total number of contacts."""
        return Contact.query.count()

    def get_dashboard_statistics(self):
        """Get statistics for the contacts dashboard."""
        total_contacts = self.get_total_contacts()

        return {
            "total_contacts": total_contacts,
            "with_opportunities": db.session.query(Contact).filter(Contact.opportunity_relationships.any()).count(),
            "with_companies": db.session.query(Contact).filter(Contact.company_id.isnot(None)).count(),
            "with_skills": db.session.query(Contact).filter(Contact.skill_level.isnot(None)).count(),
        }

    def get_top_contacts(self, limit=5):
        """Get top contacts by opportunity count."""
        return (
            db.session.query(Contact, func.count(Contact.opportunity_relationships).label("opportunity_count"))
            .outerjoin(Contact.opportunity_relationships)
            .group_by(Contact.id)
            .order_by(func.count(Contact.opportunity_relationships).desc())
            .limit(limit)
            .all()
        )

    def get_skill_segments(self):
        """Get contact segments by skill level."""
        total_contacts = self.get_total_contacts()

        # Expert level
        expert_count = (
            db.session.query(Contact).filter(Contact.skill_level == "Expert").count()
        )

        # Advanced level
        advanced_count = (
            db.session.query(Contact).filter(Contact.skill_level == "Advanced").count()
        )

        # Intermediate level
        intermediate_count = (
            db.session.query(Contact).filter(Contact.skill_level == "Intermediate").count()
        )

        # Beginner level
        beginner_count = (
            db.session.query(Contact).filter(Contact.skill_level == "Beginner").count()
        )

        return [
            {
                "name": "Expert",
                "count": expert_count,
                "percentage": self._calculate_percentage(expert_count, total_contacts),
            },
            {
                "name": "Advanced",
                "count": advanced_count,
                "percentage": self._calculate_percentage(advanced_count, total_contacts),
            },
            {
                "name": "Intermediate",
                "count": intermediate_count,
                "percentage": self._calculate_percentage(intermediate_count, total_contacts),
            },
            {
                "name": "Beginner",
                "count": beginner_count,
                "percentage": self._calculate_percentage(beginner_count, total_contacts),
            },
        ]

    def prepare_growth_data(self, months_back=6):
        """Prepare growth data for the chart."""
        months = []
        new_contacts = []
        total_contacts = []

        current_month = datetime.now().month
        current_year = datetime.now().year

        for i in range(months_back):
            month = (current_month - i) % 12
            if month == 0:
                month = 12
            year = current_year - ((current_month - i) // 12)

            # Month name for label
            month_name = datetime(year, month, 1).strftime("%b %Y")

            # Start of month date
            start_date = datetime(year, month, 1)

            # End of month date - first day of next month
            next_month = month + 1 if month < 12 else 1
            next_year = year if month < 12 else year + 1
            end_date = datetime(next_year, next_month, 1)

            # New contacts in this month
            new_in_month = Contact.query.filter(Contact.created_at >= start_date, Contact.created_at < end_date).count()

            # Total contacts at end of month
            total_at_month_end = Contact.query.filter(Contact.created_at < end_date).count()

            months.append(month_name)
            new_contacts.append(new_in_month)
            total_contacts.append(total_at_month_end)

        # Reverse lists to display chronologically
        months.reverse()
        new_contacts.reverse()
        total_contacts.reverse()

        return {"labels": months, "new_contacts": new_contacts, "total_contacts": total_contacts}

    def get_skill_distribution(self):
        """Get distribution of contacts by skill level."""
        return db.session.query(Contact.skill_level, func.count(Contact.id).label("count")).group_by(Contact.skill_level).all()

    def get_skill_area_distribution(self):
        """Get distribution of contacts by skill area."""
        return (
            db.session.query(Contact.primary_skill_area, func.count(Contact.id).label("count"))
            .filter(Contact.primary_skill_area.isnot(None))
            .group_by(Contact.primary_skill_area)
            .all()
        )

    def get_statistics(self):
        """Get comprehensive statistics for the statistics page."""
        total_contacts = self.get_total_contacts()

        # Contacts with opportunities
        with_opportunities = db.session.query(Contact).filter(Contact.opportunity_relationships.any()).count()

        # Contacts with companies
        with_companies = db.session.query(Contact).filter(Contact.company_id.isnot(None)).count()

        # Contacts with skills
        with_skills = db.session.query(Contact).filter(Contact.skill_level.isnot(None)).count()

        # Contacts with no engagement
        no_engagement = db.session.query(Contact).filter(~Contact.opportunity_relationships.any()).count()

        return {
            "total_contacts": total_contacts,
            "with_opportunities": with_opportunities,
            "with_companies": with_companies,
            "with_skills": with_skills,
            "no_engagement": no_engagement,
        }

    def _calculate_percentage(self, count, total):
        """Calculate percentage with safety check for division by zero."""
        if total == 0:
            return 0
        return round((count / total) * 100)