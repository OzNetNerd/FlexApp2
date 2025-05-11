from app.models.pages.contact import Contact
from app.models.base import db
from app.services.crud_service import CRUDService
from datetime import datetime
import random


class ContactService(CrudService):
    def __init__(self):
        super().__init__(Contact)

    def get_stats(self):
        total_contacts = Contact.query.count()

        return {
            "total_contacts": total_contacts,
            "with_opportunities": db.session.query(Contact).filter(
                Contact.opportunity_relationships.any()).distinct().count(),
            "with_skills": db.session.query(Contact).filter(Contact.skill_level.isnot(None)).count(),
            "with_companies": db.session.query(Contact).filter(Contact.company_id.isnot(None)).count(),
        }

    def get_top_contacts(self, limit=5):
        return (
            db.session.query(Contact, db.func.count(Contact.opportunity_relationships).label("opportunity_count"))
            .outerjoin(Contact.opportunity_relationships)
            .group_by(Contact.id)
            .order_by(db.func.count(Contact.opportunity_relationships).desc())
            .limit(limit)
            .all()
        )

    def get_skill_segments(self):
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

    def get_filtered_contacts(self, has_opportunities=None, has_company=None, skill_level=None):
        query = Contact.query

        if has_opportunities == "yes":
            query = query.filter(Contact.opportunity_relationships.any())
        elif has_opportunities == "no":
            query = query.filter(~Contact.opportunity_relationships.any())

        if has_company == "yes":
            query = query.filter(Contact.company_id.isnot(None))
        elif has_company == "no":
            query = query.filter(Contact.company_id.is_(None))

        if skill_level and skill_level != "all":
            query = query.filter(Contact.skill_level == skill_level)

        return query.order_by(Contact.last_name.asc(), Contact.first_name.asc()).all()

    def get_skill_distribution(self):
        return db.session.query(Contact.skill_level, db.func.count(Contact.id).label("count")).group_by(
            Contact.skill_level).all()

    def get_skill_area_distribution(self):
        return (
            db.session.query(Contact.primary_skill_area, db.func.count(Contact.id).label("count"))
            .filter(Contact.primary_skill_area.isnot(None))
            .group_by(Contact.primary_skill_area)
            .all()
        )

    @staticmethod
    def _calculate_percentage(count, total):
        if total == 0:
            return 0
        return round((count / total) * 100)