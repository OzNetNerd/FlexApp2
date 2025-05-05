"""
Core domain entities for the capability domain.

This module contains the business entities representing capabilities and their categories,
completely decoupled from any persistence or infrastructure concerns.
"""
from typing import List, Optional
from dataclasses import dataclass, field
from uuid import UUID

from domain.shared.interfaces.entity import Entity


@dataclass(frozen=True)
class CapabilityCategory(Entity):
    """
    A category that groups related capabilities.

    Attributes:
        id: Unique identifier for the category.
        name: The display name of the category.
    """
    id: UUID
    name: str


@dataclass
class Capability(Entity):
    """
    Represents a specific capability or skill that a company can possess.

    Attributes:
        id: Unique identifier for the capability.
        name: Name of the capability.
        category: The category this capability belongs to.
        category_id: Reference to the category UUID (for persistence).
    """
    id: UUID
    name: str
    category: Optional[CapabilityCategory] = None
    category_id: Optional[UUID] = None

    def assign_to_category(self, category: CapabilityCategory) -> None:
        """
        Assigns this capability to a specific category.

        Args:
            category: The category to assign this capability to.
        """
        self.category = category
        self.category_id = category.id

    def __repr__(self) -> str:
        return f"Capability(id={self.id}, name='{self.name}')"


@dataclass
class CompanyCapability:
    """
    Represents the association between a company and a capability it possesses.

    This is a many-to-many relationship entity connecting companies and capabilities.

    Attributes:
        company_id: Reference to a company.
        capability_id: Reference to a capability.
        proficiency_level: Optional rating of the company's proficiency.
    """
    company_id: UUID
    capability_id: UUID
    proficiency_level: Optional[int] = None

    def __repr__(self) -> str:
        return f"CompanyCapability(company_id={self.company_id}, capability_id={self.capability_id})"