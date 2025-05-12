# app/models/mixins.py

from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.ext.declarative import declared_attr

from app.models.base import db
from app.utils.app_logging import get_logger

logger = get_logger()


class ValidatorMixin:
    """Mixin providing validation methods for create and update."""

    def validate_create(self, data: dict) -> list:
        """
        Override this method in your model to provide creation validation.

        Args:
            data (dict): Input data.

        Returns:
            list: Validation error messages.
        """
        return []

    def validate_update(self, data: dict) -> list:
        """
        Override this method in your model to provide update validation.

        Args:
            data (dict): Updated data.

        Returns:
            list: Validation error messages.
        """
        return []


class NotableMixin:
    """Mixin for models with polymorphic relationships via notable_type and notable_id."""

    notable_type = db.Column(db.String(50), nullable=False)
    notable_id = db.Column(db.Integer, nullable=False)

    @property
    def notable(self):
        """Resolve the actual related object based on notable_type.

        Returns:
            Model or None: The linked object instance.
        """
        # Lazy import models to avoid circular references
        from app.models import Company, Contact, Opportunity, User
        # from app.models import Company, Contact, Opportunity, User

        mapping = {"Company": Company, "Contact": Contact, "Opportunity": Opportunity, "User": User}

        model = mapping.get(self.notable_type)
        return model.query.get(self.notable_id) if model else None


class TimezoneMixin:
    """Mixin for models requiring timezone-aware datetime fields."""

    @staticmethod
    def now_utc():
        """Get current UTC time with timezone info.

        Returns:
            datetime: Current UTC time with timezone info.
        """
        return datetime.now(ZoneInfo("UTC"))

    @declared_attr
    def created_at(cls):
        return db.Column(db.DateTime(timezone=True), default=cls.now_utc)

    @declared_attr
    def updated_at(cls):
        return db.Column(db.DateTime(timezone=True), default=cls.now_utc, onupdate=cls.now_utc)


class RelationshipMixin:
    """Mixin for models that need consistent relationship handling."""

    @classmethod
    def get_entity(cls, entity_type: str, entity_id: int):
        """Get entity by type and ID.

        Args:
            entity_type: Type of entity ("user", "contact", "company", etc.)
            entity_id: ID of the entity

        Returns:
            Model or None: The entity instance if found
        """
        # Lazy import models to avoid circular references
        from app.models import Company, Contact, Opportunity, User

        type_map = {"user": User, "contact": Contact, "company": Company, "opportunity": Opportunity}

        model_class = type_map.get(entity_type.lower())
        if not model_class:
            logger.error(f"Unknown entity type: {entity_type}")
            return None

        return model_class.query.get(entity_id)
