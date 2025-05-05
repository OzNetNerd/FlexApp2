"""
SQL Implementation of Company Repository.

This module provides a concrete SQL-based implementation of the CompanyRepository
interface using SQLAlchemy for database operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.domain.company.entities import Company
from src.domain.company.repositories import CompanyRepository
from src.domain.company.exceptions import CompanyNotFoundError, CompanyOperationError
from src.infrastructure.persistence.models.company import CompanyModel
from src.infrastructure.persistence.models.capability import CapabilityModel
from src.infrastructure.persistence.models.shared import CompanyCapabilityModel
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class SQLCompanyRepository(CompanyRepository):
    """SQL implementation of the CompanyRepository interface."""

    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def add(self, company: Company) -> Company:
        """
        Add a new company to the database.

        Args:
            company: Company domain entity to add

        Returns:
            Company with ID assigned

        Raises:
            CompanyOperationError: If database operation fails
        """
        try:
            # Convert domain entity to database model
            company_model = CompanyModel(
                name=company.name,
                industry=company.industry,
                website=company.website,
                address=company.address,
                description=company.description,
                primary_contact_id=company.primary_contact_id if hasattr(company, "primary_contact_id") else None,
            )

            # Add to session
            self.session.add(company_model)
            self.session.flush()  # Get ID without committing transaction

            # Add capabilities if any
            if hasattr(company, "capabilities") and company.capabilities:
                for capability_id in company.capabilities:
                    company_capability = CompanyCapabilityModel(company_id=company_model.id, capability_id=capability_id)
                    self.session.add(company_capability)

            # Update domain entity with generated ID
            company.id = company_model.id
            return company

        except SQLAlchemyError as e:
            logger.error(f"Error adding company: {str(e)}")
            raise CompanyOperationError(f"Failed to add company: {str(e)}")

    def get_by_id(self, company_id: int) -> Optional[Company]:
        """
        Get a company by its ID.

        Args:
            company_id: ID of company to retrieve

        Returns:
            Company domain entity or None if not found
        """
        try:
            company_model = self.session.query(CompanyModel).filter(CompanyModel.id == company_id).first()

            if not company_model:
                return None

            return self._map_to_entity(company_model)

        except SQLAlchemyError as e:
            logger.error(f"Error retrieving company {company_id}: {str(e)}")
            return None

    def get_all(self) -> List[Company]:
        """
        Get all companies.

        Returns:
            List of company domain entities
        """
        try:
            company_models = self.session.query(CompanyModel).all()
            return [self._map_to_entity(model) for model in company_models]

        except SQLAlchemyError as e:
            logger.error(f"Error retrieving all companies: {str(e)}")
            return []

    def update(self, company: Company) -> Company:
        """
        Update an existing company.

        Args:
            company: Company domain entity with updated values

        Returns:
            Updated company domain entity

        Raises:
            CompanyNotFoundError: If company doesn't exist
            CompanyOperationError: If database operation fails
        """
        try:
            company_model = self.session.query(CompanyModel).filter(CompanyModel.id == company.id).first()

            if not company_model:
                raise CompanyNotFoundError(f"Company with ID {company.id} not found")

            # Update basic fields
            company_model.name = company.name
            company_model.industry = company.industry
            company_model.website = company.website
            company_model.address = company.address
            company_model.description = company.description

            if hasattr(company, "primary_contact_id"):
                company_model.primary_contact_id = company.primary_contact_id

            # Update capabilities if present
            if hasattr(company, "capabilities"):
                # Remove existing capabilities
                self.session.query(CompanyCapabilityModel).filter(CompanyCapabilityModel.company_id == company.id).delete()

                # Add new capabilities
                for capability_id in company.capabilities:
                    company_capability = CompanyCapabilityModel(company_id=company.id, capability_id=capability_id)
                    self.session.add(company_capability)

            return company

        except SQLAlchemyError as e:
            logger.error(f"Error updating company {company.id}: {str(e)}")
            raise CompanyOperationError(f"Failed to update company: {str(e)}")

    def delete(self, company_id: int) -> bool:
        """
        Delete a company by ID.

        Args:
            company_id: ID of company to delete

        Returns:
            True if company was deleted, False otherwise
        """
        try:
            # Delete related company capabilities first
            self.session.query(CompanyCapabilityModel).filter(CompanyCapabilityModel.company_id == company_id).delete()

            # Delete the company
            result = self.session.query(CompanyModel).filter(CompanyModel.id == company_id).delete()

            return result > 0

        except SQLAlchemyError as e:
            logger.error(f"Error deleting company {company_id}: {str(e)}")
            return False

    def get_by_name(self, name: str) -> List[Company]:
        """
        Get companies by name search.

        Args:
            name: Full or partial company name to search

        Returns:
            List of matching company domain entities
        """
        try:
            company_models = self.session.query(CompanyModel).filter(CompanyModel.name.ilike(f"%{name}%")).all()

            return [self._map_to_entity(model) for model in company_models]

        except SQLAlchemyError as e:
            logger.error(f"Error searching companies by name '{name}': {str(e)}")
            return []

    def get_by_capability(self, capability_id: int) -> List[Company]:
        """
        Get companies with a specific capability.

        Args:
            capability_id: ID of capability to filter by

        Returns:
            List of company domain entities with the specified capability
        """
        try:
            company_models = (
                self.session.query(CompanyModel)
                .join(CompanyCapabilityModel, CompanyModel.id == CompanyCapabilityModel.company_id)
                .filter(CompanyCapabilityModel.capability_id == capability_id)
                .all()
            )

            return [self._map_to_entity(model) for model in company_models]

        except SQLAlchemyError as e:
            logger.error(f"Error retrieving companies by capability {capability_id}: {str(e)}")
            return []

    def _map_to_entity(self, model: CompanyModel) -> Company:
        """
        Map database model to domain entity.

        Args:
            model: Database model to map

        Returns:
            Company domain entity
        """
        # Create the base company entity
        company = Company(
            id=model.id,
            name=model.name,
            industry=model.industry,
            website=model.website,
            address=model.address,
            description=model.description,
        )

        # Set primary contact if exists
        if model.primary_contact_id:
            company.primary_contact_id = model.primary_contact_id

        # Get capabilities
        try:
            capability_models = self.session.query(CompanyCapabilityModel).filter(CompanyCapabilityModel.company_id == model.id).all()

            company.capabilities = [cm.capability_id for cm in capability_models]

        except SQLAlchemyError as e:
            logger.warning(f"Error loading capabilities for company {model.id}: {str(e)}")
            company.capabilities = []

        return company
