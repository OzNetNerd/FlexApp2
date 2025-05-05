"""GraphQL queries for User domain model."""

import strawberry
from typing import List, Optional
from .types import User
from domain.user.repositories import UserRepository
from infrastructure.persistence.repositories.user_repository import SQLAlchemyUserRepository


@strawberry.type
class UserQueries:
    """GraphQL queries for users."""

    def __init__(self):
        """Initialize with repository."""
        self.repository: UserRepository = SQLAlchemyUserRepository()

    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            id: User ID to retrieve

        Returns:
            User if found, None otherwise
        """
        entity = self.repository.get_by_id(id)
        return User.from_entity(entity) if entity else None

    @strawberry.field
    def users(self) -> List[User]:
        """
        Get all users.

        Returns:
            List of all users
        """
        entities = self.repository.get_all()
        return [User.from_entity(entity) for entity in entities]