"""GraphQL type definitions for User domain model."""

import strawberry
from typing import Optional
from domain.user.entities import User as UserEntity


@strawberry.type
class User:
    """
    GraphQL User type representation.

    Attributes:
        id: Unique identifier
        username: Login username
        name: Full name
        email: Email address
        is_admin: Admin status
        created_at: Creation timestamp
        updated_at: Last update timestamp
        related_users: Related users JSON
        related_companies: Related companies JSON
    """
    id: int
    username: str
    name: str
    email: str
    is_admin: bool
    created_at: str
    updated_at: Optional[str]
    related_users: Optional[str]
    related_companies: Optional[str]

    @classmethod
    def from_entity(cls, entity: UserEntity) -> "User":
        """
        Convert domain entity to GraphQL type.

        Args:
            entity: Domain entity to convert

        Returns:
            GraphQL type representation
        """
        return cls(
            id=entity.id,
            username=entity.username,
            name=entity.name,
            email=entity.email,
            is_admin=entity.is_admin,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            related_users=entity.related_users,
            related_companies=entity.related_companies
        )