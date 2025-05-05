"""User repository interface defining data access methods."""

from typing import Optional, List
from domain.shared.interfaces.repository import Repository
from .entities import User


class UserRepository(Repository):
    """Repository interface for User entities."""

    def get_by_id(self, id: int) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            id: The user ID to retrieve

        Returns:
            User if found, None otherwise
        """
        pass

    def get_all(self) -> List[User]:
        """
        Get all users.

        Returns:
            List of all users
        """
        pass

    def add(self, user: User) -> User:
        """
        Add a new user.

        Args:
            user: User to add

        Returns:
            Added user with new ID
        """
        pass

    def update(self, user: User) -> User:
        """
        Update an existing user.

        Args:
            user: User to update

        Returns:
            Updated user
        """
        pass

    def delete(self, id: int) -> bool:
        """
        Delete a user.

        Args:
            id: ID of user to delete

        Returns:
            True if deleted, False otherwise
        """
        pass

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: Username to search for

        Returns:
            User if found, None otherwise
        """
        pass

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: Email to search for

        Returns:
            User if found, None otherwise
        """
        pass