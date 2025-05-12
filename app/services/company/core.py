# app/services/company/core.py

from app.models.pages.company import Company
from app.services.service_base import CRUDService
from app.services.validator_mixin import ValidatorMixin


class CompanyCoreService(CRUDService, ValidatorMixin):
    """Core service for Company CRUD operations."""

    def __init__(self):
        """Initialize the Company core service."""
        super().__init__(model_class=Company)

    def get_filtered_companies(self, filters):
        """Get companies based on filter criteria."""
        query = self.model_class.query

        # Filter by opportunities
        if filters.get("has_opportunities") == "yes":
            query = query.filter(self.model_class.opportunities.any())
        elif filters.get("has_opportunities") == "no":
            query = query.filter(~self.model_class.opportunities.any())

        # Filter by contacts
        if filters.get("has_contacts") == "yes":
            query = query.filter(self.model_class.contacts.any())
        elif filters.get("has_contacts") == "no":
            query = query.filter(~self.model_class.contacts.any())

        # Filter by capabilities
        if filters.get("has_capabilities") == "yes":
            query = query.filter(self.model_class.company_capabilities.any())
        elif filters.get("has_capabilities") == "no":
            query = query.filter(~self.model_class.company_capabilities.any())

        return query.order_by(self.model_class.name.asc()).all()