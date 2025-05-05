"""GraphQL types for customer operations."""

import strawberry
from typing import List, Optional
from datetime import datetime


@strawberry.type
class Customer:
    """
    GraphQL Customer type.

    GraphQL representation of a customer in the system.
    """
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    company_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto) -> 'Customer':
        """
        Create a GraphQL Customer from a CustomerDTO.

        Args:
            dto: The CustomerDTO to convert.

        Returns:
            A GraphQL Customer type.
        """
        return cls(
            id=dto.id,
            name=dto.name,
            email=dto.email,
            phone=dto.phone,
            company_id=dto.company_id,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )


@strawberry.input
class CreateCustomerInput:
    """Input type for creating a customer."""
    name: str
    email: str
    phone: Optional[str] = None
    company_id: Optional[int] = None


@strawberry.input
class UpdateCustomerInput:
    """Input type for updating a customer."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company_id: Optional[int] = None