from app.services.service_base import BaseFeatureService
from app.models.pages.company import Company


class CompanyService(BaseFeatureService):
    def __init__(self):
        super().__init__(Company)

    def get_dashboard_statistics(self):
        """Get company dashboard statistics."""
        stats = super().get_dashboard_statistics()
        stats.update({
            "total_companies": Company.query.count(),
            "with_opportunities": self.count_with_opportunities(),
            "with_contacts": self.count_with_contacts()
        })
        return stats

    def count_with_opportunities(self):
        """Count companies with opportunities."""
        return Company.query.filter(Company.opportunities.any()).count()

    def count_with_contacts(self):
        """Count companies with contacts."""
        return Company.query.filter(Company.contacts.any()).count()

    def get_statistics(self):
        """Get company statistics."""
        return {
            "total_companies": Company.query.count(),
            "with_opportunities": self.count_with_opportunities(),
            "with_contacts": self.count_with_contacts(),
            "no_engagement": self.count_no_engagement()
        }

    def count_no_engagement(self):
        """Count companies with no engagement."""
        return Company.query.filter(~Company.opportunities.any(), ~Company.contacts.any()).count()