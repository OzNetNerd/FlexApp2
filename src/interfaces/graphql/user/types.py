"""GraphQL types for user operations."""

import strawberry
from typing import Optional
from domain.user.entities import User as UserEntity
from application.user.dto import UserDTO


@strawberry.type
class User:
    """GraphQL User type representation."""
    id: int
    username: str
    name: str
    email: str
    is_admin: bool
    created_at: str
    updated_at: Optional[str] = None
    related_users: Optional[str] = None
    related_companies: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: UserEntity) -> "User":
        """Convert domain entity to GraphQL type."""
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

    @classmethod
    def from_dto(cls, dto: UserDTO) -> "User":
        """Convert DTO to GraphQL type."""
        return cls(
            id=dto.id,
            username=dto.username,
            name=dto.name,
            email=dto.email,
            is_admin=dto.is_admin,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            related_users=dto.related_users,
            related_companies=dto.related_companies
        )


@strawberry.input
class CreateUserInput:
    """Input type for creating a user."""
    username: str
    name: str
    email: str
    password: str
    is_admin: Optional[bool] = False


@strawberry.input
class UpdateUserInput:
    """Input type for updating a user."""
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None