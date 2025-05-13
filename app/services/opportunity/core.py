# app/services/opportunity/core.py
from app.models import Opportunity
from app.services.service_base import CRUDService
from app.services.validator_mixin import ValidatorMixin


class OpportunityCoreService(CRUDService, ValidatorMixin):
    """Core service for Opportunity CRUD operations."""

    def __init__(self):
        """Initialize the Opportunity core service."""
        super().__init__(model_class=Opportunity)

    def get_filtered_opportunities(self, status=None, stage=None, priority=None):
        """Get filtered opportunities based on criteria."""
        query = self.model_class.query

        if status:
            query = query.filter_by(status=status)

        if stage:
            query = query.filter_by(stage=stage)

        if priority:
            query = query.filter_by(priority=priority)

        return query.order_by(self.model_class.close_date.asc()).all()

    def get_hot_opportunities(self, limit=5):
        """Get hot opportunities with high priority."""
        return (
            self.model_class.query.filter_by(status="active", priority="high")
            .order_by(self.model_class.close_date.asc())
            .limit(limit)
            .all()
        )
