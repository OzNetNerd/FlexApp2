"""
SQLAlchemy implementation of capability repositories.

These repositories implement the domain repository interfaces using SQLAlchemy models.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm.exc import NoResultFound

from src.domain.capability.entities import Capability as DomainCapability
from src.domain.capability.entities import CapabilityCategory as DomainCapabilityCategory
from src.domain.capability.entities import CompanyCapability as DomainCompanyCapability
from src.domain.capability.repositories import CapabilityRepository, CapabilityCategoryRepository
from src.infrastructure.persistence.models.base import db
from src.infrastructure.persistence.models.capability import (
    Capability as CapabilityModel,
    CapabilityCategory as CapabilityCategoryModel,
    CompanyCapability as CompanyCapabilityModel,
)
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class SQLAlchemyCapabilityRepository(CapabilityRepository):
    """
    SQLAlchemy implementation of the capability repository.

    Translates between domain entities and database models.
    """

    def get_by_id(self, capability_id: UUID) -> Optional[DomainCapability]:
        """
        Retrieves a capability by its unique identifier.

        Args:
            capability_id: The unique identifier of the capability.

        Returns:
            The domain capability if found, None otherwise.
        """
        model = CapabilityModel.query.get(int(capability_id))
        if not model:
            return None

        return self._to_domain_entity(model)

    def get_all(self) -> List[DomainCapability]:
        """
        Retrieves all capabilities.

        Returns:
            A list of all domain capabilities.
        """
        models = CapabilityModel.query.all()
        return [self._to_domain_entity(model) for model in models]

    def save(self, capability: DomainCapability) -> DomainCapability:
        """
        Persists a capability to the database.

        Args:
            capability: The domain capability to save.

        Returns:
            The saved domain capability.
        """
        try:
            model = CapabilityModel.query.get(int(capability.id))
            if not model:
                model = CapabilityModel(
                    id=int(capability.id), name=capability.name, category_id=int(capability.category_id) if capability.category_id else None
                )
            else:
                model.name = capability.name
                model.category_id = int(capability.category_id) if capability.category_id else None

            db.session.add(model)
            db.session.commit()

            # Refresh the domain entity with any updates
            return self._to_domain_entity(model)

        except Exception as e:
            logger.error(f"Error saving capability: {e}")
            db.session.rollback()
            raise

    def delete(self, capability_id: UUID) -> None:
        """
        Removes a capability from the database.

        Args:
            capability_id: The unique identifier of the capability to delete.
        """
        try:
            model = CapabilityModel.query.get(int(capability_id))
            if model:
                db.session.delete(model)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error deleting capability: {e}")
            db.session.rollback()
            raise

    def get_by_category(self, category_id: UUID) -> List[DomainCapability]:
        """
        Retrieves all capabilities in a specific category.

        Args:
            category_id: The unique identifier of the category.

        Returns:
            A list of domain capabilities in the specified category.
        """
        models = CapabilityModel.query.filter_by(category_id=int(category_id)).all()
        return [self._to_domain_entity(model) for model in models]

    def get_company_capabilities(self, company_id: UUID) -> List[DomainCompanyCapability]:
        """
        Retrieves all capabilities associated with a specific company.

        Args:
            company_id: The unique identifier of the company.

        Returns:
            A list of domain company-capability associations.
        """
        models = CompanyCapabilityModel.query.filter_by(company_id=int(company_id)).all()
        return [
            DomainCompanyCapability(company_id=UUID(int=model.company_id), capability_id=UUID(int=model.capability_id)) for model in models
        ]

    def _to_domain_entity(self, model: CapabilityModel) -> DomainCapability:
        """
        Converts a database model to a domain entity.

        Args:
            model: The database model.

        Returns:
            The corresponding domain entity.
        """
        category = None
        if model.category:
            category = DomainCapabilityCategory(id=UUID(int=model.category.id), name=model.category.name)

        return DomainCapability(
            id=UUID(int=model.id),
            name=model.name,
            category=category,
            category_id=UUID(int=model.category_id) if model.category_id else None,
        )


class SQLAlchemyCapabilityCategoryRepository(CapabilityCategoryRepository):
    """SQLAlchemy implementation of the capability category repository."""

    def get_by_id(self, category_id: UUID) -> Optional[DomainCapabilityCategory]:
        """Gets a category by ID."""
        model = CapabilityCategoryModel.query.get(int(category_id))
        if not model:
            return None

        return self._to_domain_entity(model)

    def get_all(self) -> List[DomainCapabilityCategory]:
        """Gets all categories."""
        models = CapabilityCategoryModel.query.all()
        return [self._to_domain_entity(model) for model in models]

    def save(self, category: DomainCapabilityCategory) -> DomainCapabilityCategory:
        """Saves a category."""
        try:
            model = CapabilityCategoryModel.query.get(int(category.id))
            if not model:
                model = CapabilityCategoryModel(id=int(category.id), name=category.name)
            else:
                model.name = category.name

            db.session.add(model)
            db.session.commit()

            return self._to_domain_entity(model)

        except Exception as e:
            logger.error(f"Error saving capability category: {e}")
            db.session.rollback()
            raise

    def delete(self, category_id: UUID) -> None:
        """Deletes a category."""
        try:
            model = CapabilityCategoryModel.query.get(int(category_id))
            if model:
                db.session.delete(model)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error deleting capability category: {e}")
            db.session.rollback()
            raise

    def _to_domain_entity(self, model: CapabilityCategoryModel) -> DomainCapabilityCategory:
        """Converts a database model to a domain entity."""
        return DomainCapabilityCategory(id=UUID(int=model.id), name=model.name)
