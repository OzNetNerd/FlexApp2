"""User repository interface defining data access methods."""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.shared.interfaces.repository import Repository
from src.domain.user.entities import User


class UserRepository(Repository[User], ABC):
    """
    Repository interface for User entity operations.

    Defines the contract for user persistence operations.
    """

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[User]:
        """Get a user by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        """Get all users."""
        pass

    @abstractmethod
    def add(self, user: User) -> User:
        """Add a new user."""
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """Update an existing user."""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete a user."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        pass

    @abstractmethod
    def search_by_username(self, query: str) -> List[User]:
        """Search for users by username pattern match."""
        pass