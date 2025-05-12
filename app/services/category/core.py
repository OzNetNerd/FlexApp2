# app/services/category/core.py
from app.models.pages.srs import Category
from app.services.service_base import CRUDService
from app.services.validator_mixin import ValidatorMixin
from app.utils.app_logging import get_logger

logger = get_logger()


class CategoryCoreService(CRUDService, ValidatorMixin):
    """Core service for Category CRUD operations."""

    def __init__(self):
        """Initialize the Category core service."""
        super().__init__(model_class=Category)

    def validate_create(self, data: dict) -> list[str]:
        """Validate category creation data."""
        errors = []
        if not data.get('name'):
            errors.append("Category name is required")
        return errors

    def validate_update(self, entity, data: dict) -> list[str]:
        """Validate category update data."""
        return self.validate_create(data)