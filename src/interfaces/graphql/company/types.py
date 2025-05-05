"""
GraphQL type definitions for Company domain entities.

This module defines the GraphQL types that represent Company domain
entities and their relationships in the GraphQL schema.
"""
import strawberry
from typing import List, Optional
from datetime import datetime

from application.company.dto import CompanyDTO, CompanyDetailsDTO
from interfaces.graphql.customer.types import Customer


@strawberry.type
class Company:
    """
    GraphQL representation of a Company entity.

    This type represents the basic properties of a company and
    provides resolver methods for related entities.
    """
    id: int
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def customers(self, info) -> List['Customer']:
        """
        Resolve the customers associated with this company.

        Args:
            info: GraphQL resolver info containing the request context

        Returns:
            List[Customer]: List of customers associated with this company
        """
        return await info.context.loaders.customer_loader.load_by_company_id(self.id)


@strawberry.input
class CompanyInput:
    """
    GraphQL input type for creating or updating a Company.

    This type defines the fields that can be provided when
    creating or updating a company through GraphQL mutations.
    """
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None


@strawberry.type
class CompanyDetails(Company):
    """
    Extended GraphQL representation of a Company with additional details.

    This type includes all fields from the base Company type and adds
    additional detailed information that might not be needed in all contexts.
    """
    description: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None

    @classmethod
    def from_dto(cls, dto: CompanyDetailsDTO) -> 'CompanyDetails':
        """
        Create a CompanyDetails GraphQL type from a DTO.

        Args:
            dto: The CompanyDetailsDTO to convert

        Returns:
            CompanyDetails: The GraphQL type with data from the DTO
        """
        return cls(
            id=dto.id,
            name=dto.name,
            website=dto.website,
            industry=dto.industry,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            description=dto.description,
            employee_count=dto.employee_count,
            annual_revenue=dto.annual_revenue
        )