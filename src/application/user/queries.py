"""User query handlers."""

from typing import List, Optional
from src.domain.user.repositories import UserRepository
from application.user.dto import UserDTO


class UserQueryHandler:
    """
    Query handler for user data.

    Handles queries that retrieve user data.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the query handler.

        Args:
            user_repository: Repository for user persistence.
        """
        self.user_repository = user_repository

    def get_user_by_id(self, id: int) -> Optional[UserDTO]:
        """
        Get a user by ID.

        Args:
            id: The user ID to retrieve.

        Returns:
            A DTO of the user or None if not found.
        """
        user = self.user_repository.get_by_id(id)
        if not user:
            return None
        return UserDTO.from_entity(user)

    def get_all_users(self) -> List[UserDTO]:
        """
        Get all users.

        Returns:
            A list of user DTOs.
        """
        users = self.user_repository.get_all()
        return [UserDTO.from_entity(user) for user in users]

    def search_users_by_username(self, query: str) -> List[UserDTO]:
        """
        Search for users by username.

        Args:
            query: The search string to match against usernames.

        Returns:
            A list of user DTOs matching the search criteria.
        """
        users = self.user_repository.search_by_username(query)
        return [UserDTO.from_entity(user) for user in users]
