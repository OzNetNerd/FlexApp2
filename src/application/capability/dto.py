"""
Data Transfer Objects for the capability domain.

These classes facilitate data exchange between the domain and interface layers.
"""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID


@dataclass
class CapabilityCategoryDTO:
    """
    DTO for capability categories.

    Attributes:
        id: Category ID (None for new categories).
        name: Category name.
    """

    name: str
    id: Optional[UUID] = None


@dataclass
class CapabilityDTO:
    """
    DTO for capabilities.

    Attributes:
        id: Capability ID (None for new capabilities).
        name: Capability name.
        category_id: ID of the category this capability belongs to.
        category_name: Name of the category (optional, for display purposes).
    """

    name: str
    category_id: UUID
    id: Optional[UUID] = None
    category_name: Optional[str] = None


@dataclass
class CompanyCapabilityDTO:
    """
    DTO for company-capability associations.

    Attributes:
        company_id: ID of the company.
        capability_id: ID of the capability.
        capability_name: Name of the capability (optional, for display).
        category_name: Name of the category (optional, for display).
    """

    company_id: UUID
    capability_id: UUID
    capability_name: Optional[str] = None
    category_name: Optional[str] = None
