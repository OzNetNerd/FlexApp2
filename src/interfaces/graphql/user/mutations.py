"""GraphQL mutations for User domain model."""

import strawberry
from typing import Optional
from .types import User
from domain.user.entities import User as UserEntity
from domain.user.repositories import UserRepository
from infrastructure.persistence.repositories.user_repository import SQLAlchemyUserRepository


@strawberry.type
class UserMutations:
    """GraphQL mutations for users."""

    def __init__(self):
        """Initialize with repository."""
        self.repository: UserRepository = SQLAlchemyUserRepository()

    @strawberry.mutation
    def create_user(
            self,
            username: str,
            name: str,
            email: str,
            is_admin: bool = False
    ) -> User:
        """
        Create a new user.

        Args:
            username: Username for new user
            name: Full name for new user
            email: Email for new user
            is_admin: Admin status for new user

        Returns:
            Newly created user
        """
        entity = UserEntity(
            id=0,  # Will be set by repository
            username=username,
            name=name,
            email=email,
            is_admin=is_admin
        )
        created = self.repository.add(entity)
        return User.from_entity(created)

    @strawberry.mutation
    def update_user(
            self,
            id: int,
            username: Optional[str] = None,
            name: Optional[str] = None,
            email: Optional[str] = None,
            is_admin: Optional[bool] = None
    ) -> Optional[User]:
        """
        Update an existing user.

        Args:
            id: ID of user to update
            username: New username (optional)
            name: New name (optional)
            email: New email (optional)
            is_admin: New admin status (optional)

        Returns:
            Updated user or None if not found
        """
        entity = self.repository.get_by_id(id)
        if not entity:
            return None

        if username is not None:
            entity.username = username
        if name is not None:
            entity.name = name
        if email is not None:
            entity.email = email
        if is_admin is not None:
            entity.is_admin = is_admin

        updated = self.repository.update(entity)
        return User.from_entity(updated)

    @strawberry.mutation
    def delete_user(self, id: int) -> bool:
        """
        Delete a user.

        Args:
            id: ID of user to delete

        Returns:
            True if deleted, False otherwise
        """
        return self.repository.delete(id)