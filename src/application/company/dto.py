"""
Data Transfer Objects (DTOs) for the Company domain.

This module contains DTOs that transfer company data between the domain
and application layers, following DDD principles.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class CompanyDTO:
    """
    Basic company data transfer object.

    Contains the essential properties of a company entity for use in the application layer.

    Attributes:
        id: Unique identifier for the company
        name: Company name
        website: Company website URL
        industry: Industry the company operates in
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: int
    name: str
    website: Optional[str]
    industry: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity):
        """
        Create a DTO from a domain entity.

        Args:
            entity: The company domain entity

        Returns:
            CompanyDTO: A new DTO initialized with entity data
        """
        return cls(
            id=entity.id,
            name=entity.name,
            website=entity.website,
            industry=entity.industry,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


@dataclass
class CompanyDetailsDTO(CompanyDTO):
    """
    Extended company data transfer object with additional details.

    Contains all basic company properties plus additional detailed information.

    Attributes:
        description: Detailed description of the company
        employee_count: Number of employees at the company
        annual_revenue: Annual revenue of the company
    """

    description: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None

    @classmethod
    def from_entity(cls, entity):
        """
        Create a detailed DTO from a domain entity.

        Args:
            entity: The company domain entity with details

        Returns:
            CompanyDetailsDTO: A new detailed DTO initialized with entity data
        """
        return cls(
            id=entity.id,
            name=entity.name,
            website=entity.website,
            industry=entity.industry,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            description=getattr(entity, "description", None),
            employee_count=getattr(entity, "employee_count", None),
            annual_revenue=getattr(entity, "annual_revenue", None),
        )
