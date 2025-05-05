"""
Repository interfaces for the capability domain.

Defines the contracts that infrastructure implementations must fulfill.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.capability.entities import Capability, CapabilityCategory, CompanyCapability


class CapabilityRepository(ABC):
    """
    Repository interface for capability-related operations.

    Implementations must provide concrete storage mechanisms while
    adhering to this contract.
    """

    @abstractmethod
    def get_by_id(self, capability_id: UUID) -> Optional[Capability]:
        """
        Retrieves a capability by its unique identifier.

        Args:
            capability_id: The unique identifier of the capability.

        Returns:
            The capability if found, None otherwise.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Capability]:
        """
        Retrieves all capabilities.

        Returns:
            A list of all capabilities.
        """
        pass

    @abstractmethod
    def save(self, capability: Capability) -> Capability:
        """
        Persists a capability to the storage.

        Args:
            capability: The capability to save.

        Returns:
            The saved capability with any updates (like assigned ID).
        """
        pass

    @abstractmethod
    def delete(self, capability_id: UUID) -> None:
        """
        Removes a capability from the storage.

        Args:
            capability_id: The unique identifier of the capability to delete.
        """
        pass

    @abstractmethod
    def get_by_category(self, category_id: UUID) -> List[Capability]:
        """
        Retrieves all capabilities in a specific category.

        Args:
            category_id: The unique identifier of the category.

        Returns:
            A list of capabilities in the specified category.
        """
        pass

    @abstractmethod
    def get_company_capabilities(self, company_id: UUID) -> List[CompanyCapability]:
        """
        Retrieves all capabilities associated with a specific company.

        Args:
            company_id: The unique identifier of the company.

        Returns:
            A list of company-capability associations.
        """
        pass


class CapabilityCategoryRepository(ABC):
    """Repository interface for capability category operations."""

    @abstractmethod
    def get_by_id(self, category_id: UUID) -> Optional[CapabilityCategory]:
        """Gets a category by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[CapabilityCategory]:
        """Gets all categories."""
        pass

    @abstractmethod
    def save(self, category: CapabilityCategory) -> CapabilityCategory:
        """Saves a category."""
        pass

    @abstractmethod
    def delete(self, category_id: UUID) -> None:
        """Deletes a category."""
        pass