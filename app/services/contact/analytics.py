# app/services/contact/analytics.py
from datetime import datetime
import random
from app.models.pages.contact import Contact
from app.models.base import db
from app.services.service_base import ServiceBase


class ContactAnalyticsService(ServiceBase):
    """Service for contact analytics and statistics."""

    def __init__(self):
        """Initialize the Contact analytics service."""
        super().__init__()

    def get_stats(self):
        """Get general contact statistics."""
        total_contacts = Contact.query.count()

        return {
            "total_contacts": total_contacts,
            "with_opportunities": db.session.query(Contact).filter(
                Contact.opportunity_relationships.any()).distinct().count(),
            "with_skills": db.session.query(Contact).filter(Contact.skill_level.isnot(None)).count(),
            "with_companies": db.session.query(Contact).filter(Contact.company_id.isnot(None)).count(),
        }

    def get_top_contacts(self, limit=5):
        """Get top contacts by opportunity count."""
        return (
            db.session.query(Contact, db.func.count(Contact.opportunity_relationships).label("opportunity_count"))
            .outerjoin(Contact.opportunity_relationships)
            .group_by(Contact.id)
            .order_by(db.func.count(Contact.opportunity_relationships).desc())
            .limit(limit)
            .all()
        )

    def get_skill_segments(self):
        """Get contact segments by skill level."""
        total_contacts = Contact.query.count()

        return [
            {
                "name": "Expert",
                "count": db.session.query(Contact).filter(Contact.skill_level == "Expert").count(),
                "percentage": self._calculate_percentage(
                    db.session.query(Contact).filter(Contact.skill_level == "Expert").count(), total_contacts),
            },
            {
                "name": "Advanced",
                "count": db.session.query(Contact).filter(Contact.skill_level == "Advanced").count(),
                "percentage": self._calculate_percentage(
                    db.session.query(Contact).filter(Contact.skill_level == "Advanced").count(), total_contacts),
            },
            {
                "name": "Intermediate",
                "count": db.session.query(Contact).filter(Contact.skill_level == "Intermediate").count(),
                "percentage": self._calculate_percentage(
                    db.session.query(Contact).filter(Contact.skill_level == "Intermediate").count(), total_contacts
                ),
            },
            {
                "name": "Beginner",
                "count": db.session.query(Contact).filter(Contact.skill_level == "Beginner").count(),
                "percentage": self._calculate_percentage(
                    db.session.query(Contact).filter(Contact.skill_level == "Beginner").count(), total_contacts),
            },
        ]

    def prepare_growth_data(self):
        """Prepare growth data for the chart."""
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

            month_name = datetime(year, month, 1).strftime("%b %Y")
            months.append(month_name)

            new_contacts.append(random.randint(5, 20))
            total_contacts.append(random.randint(50, 150))

        months.reverse()
        new_contacts.reverse()
        total_contacts.reverse()

        return {"labels": months, "new_contacts": new_contacts, "total_contacts": total_contacts}

    def get_skill_distribution(self):
        """Get distribution of contacts by skill level."""
        return db.session.query(Contact.skill_level, db.func.count(Contact.id).label("count")).group_by(
            Contact.skill_level).all()

    def get_skill_area_distribution(self):
        """Get distribution of contacts by skill area."""
        return (
            db.session.query(Contact.primary_skill_area, db.func.count(Contact.id).label("count"))
            .filter(Contact.primary_skill_area.isnot(None))
            .group_by(Contact.primary_skill_area)
            .all()
        )

    @staticmethod
    def _calculate_percentage(count, total):
        """Calculate percentage with safety check for division by zero."""
        if total == 0:
            return 0
        return round((count / total) * 100)