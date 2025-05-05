"""
Command objects and handlers for company operations.

This module contains command objects that represent user intents for operations
on company entities, as well as handlers that process these commands.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from domain.company.entities import Company
from domain.company.repositories import CompanyRepository
from domain.shared.value_objects.relationship import Relationship
from infrastructure.persistence.unit_of_work import UnitOfWork
from domain.company.events import CompanyCreated, CompanyUpdated, CompanyDeleted
from infrastructure.messaging.event_bus import EventBus


@dataclass(frozen=True)
class CreateCompanyCommand:
    """
    Command to create a new company.

    Attributes:
        name: Company name.
        industry: Company industry.
        website: Company website URL.
        address: Company physical address.
        description: Company description.
        capabilities: List of capability IDs the company has.
        primary_contact_id: ID of primary contact person.
    """
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[int]] = None
    primary_contact_id: Optional[int] = None


@dataclass(frozen=True)
class UpdateCompanyCommand:
    """
    Command to update an existing company.

    Attributes:
        id: ID of company to update.
        name: Updated company name.
        industry: Updated industry.
        website: Updated website URL.
        address: Updated physical address.
        description: Updated description.
        capabilities: Updated list of capability IDs.
        primary_contact_id: Updated primary contact ID.
    """
    id: int
    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[int]] = None
    primary_contact_id: Optional[int] = None


@dataclass(frozen=True)
class DeleteCompanyCommand:
    """
    Command to delete a company.

    Attributes:
        id: ID of company to delete.
    """
    id: int


class CompanyCommandHandler:
    """
    Handler for company-related commands.

    Processes commands by performing operations on company entities
    and related domain objects.
    """

    def __init__(
            self,
            company_repository: CompanyRepository,
            unit_of_work: UnitOfWork,
            event_bus: EventBus
    ):
        """
        Initialize command handler with required dependencies.

        Args:
            company_repository: Repository for company persistence
            unit_of_work: Unit of work for transaction management
            event_bus: Event bus for publishing domain events
        """
        self.company_repository = company_repository
        self.unit_of_work = unit_of_work
        self.event_bus = event_bus

    def handle_create_company(self, command: CreateCompanyCommand) -> int:
        """
        Handle company creation command.

        Args:
            command: Command with company creation data

        Returns:
            ID of created company
        """
        with self.unit_of_work:
            company = Company(
                name=command.name,
                industry=command.industry,
                website=command.website,
                address=command.address,
                description=command.description
            )

            # Add capabilities if provided
            if command.capabilities:
                for capability_id in command.capabilities:
                    company.add_capability(capability_id)

            # Set primary contact if provided
            if command.primary_contact_id:
                company.set_primary_contact(command.primary_contact_id)

            created_company = self.company_repository.add(company)
            self.unit_of_work.commit()

            # Publish domain event
            self.event_bus.publish(CompanyCreated(company_id=created_company.id))

            return created_company.id

    def handle_update_company(self, command: UpdateCompanyCommand) -> bool:
        """
        Handle company update command.

        Args:
            command: Command with company update data

        Returns:
            True if company was updated, False otherwise
        """
        with self.unit_of_work:
            company = self.company_repository.get_by_id(command.id)
            if not company:
                return False

            # Update basic properties
            if command.name is not None:
                company.name = command.name
            if command.industry is not None:
                company.industry = command.industry
            if command.website is not None:
                company.website = command.website
            if command.address is not None:
                company.address = command.address
            if command.description is not None:
                company.description = command.description

            # Update capabilities if provided
            if command.capabilities is not None:
                company.clear_capabilities()
                for capability_id in command.capabilities:
                    company.add_capability(capability_id)

            # Update primary contact if provided
            if command.primary_contact_id is not None:
                company.set_primary_contact(command.primary_contact_id)

            self.company_repository.update(company)
            self.unit_of_work.commit()

            # Publish domain event
            self.event_bus.publish(CompanyUpdated(company_id=company.id))

            return True

    def handle_delete_company(self, command: DeleteCompanyCommand) -> bool:
        """
        Handle company deletion command.

        Args:
            command: Command with company deletion data

        Returns:
            True if company was deleted, False otherwise
        """
        with self.unit_of_work:
            result = self.company_repository.delete(command.id)
            if result:
                self.unit_of_work.commit()

                # Publish domain event
                self.event_bus.publish(CompanyDeleted(company_id=command.id))

            return result