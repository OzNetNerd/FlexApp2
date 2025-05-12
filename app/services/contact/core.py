# app/services/contact/core.py
from app.models.pages.contact import Contact
from app.services.service_base import CRUDService
from app.services.validator_mixin import ValidatorMixin


class ContactCoreService(CRUDService, ValidatorMixin):
    """Core service for Contact CRUD operations."""

    def __init__(self):
        """Initialize the Contact core service."""
        super().__init__(model_class=Contact)

    def get_filtered_contacts(self, has_opportunities=None, has_company=None, skill_level=None):
        """Get contacts based on filter criteria."""
        query = self.model_class.query

        if has_opportunities == "yes":
            query = query.filter(self.model_class.opportunity_relationships.any())
        elif has_opportunities == "no":
            query = query.filter(~self.model_class.opportunity_relationships.any())

        if has_company == "yes":
            query = query.filter(self.model_class.company_id.isnot(None))
        elif has_company == "no":
            query = query.filter(self.model_class.company_id.is_(None))

        if skill_level and skill_level != "all":
            query = query.filter(self.model_class.skill_level == skill_level)

        return query.order_by(self.model_class.last_name.asc(), self.model_class.first_name.asc()).all()