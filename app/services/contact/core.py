# app/services/contact/core.py
from app.services.service_base import BaseFeatureService
from app.models.pages.contact import Contact


class ContactService(BaseFeatureService):
    def __init__(self):
        super().__init__(Contact)

    def get_dashboard_statistics(self):
        """Get contact dashboard statistics."""
        stats = super().get_dashboard_statistics()
        stats.update({
            "total_contacts": Contact.query.count(),
            "with_opportunities": self.count_with_opportunities(),
            "with_companies": self.count_with_companies()
        })
        return stats

    def count_with_opportunities(self):
        """Count contacts with opportunities."""
        return Contact.query.filter(Contact.opportunity_relationships.any()).count()

    def count_with_companies(self):
        """Count contacts with companies."""
        return Contact.query.filter(Contact.company_id.isnot(None)).count()

    def count_with_skills(self):
        """Count contacts with skills."""
        return Contact.query.filter(Contact.skill_level.isnot(None)).count()

    def get_statistics(self):
        """Get contact statistics."""
        return {
            "total_contacts": Contact.query.count(),
            "with_opportunities": self.count_with_opportunities(),
            "with_companies": self.count_with_companies(),
            "with_skills": self.count_with_skills(),
            "no_engagement": self.count_no_engagement()
        }

    def count_no_engagement(self):
        """Count contacts with no engagement."""
        return Contact.query.filter(~Contact.opportunity_relationships.any()).count()

    def get_filtered_contacts(self, has_opportunities=None, has_company=None, skill_level=None):
        """Get contacts based on filter criteria."""
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