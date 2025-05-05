"""User command handlers."""

from typing import Optional, Dict, Any
from src.domain.user.entities import User
from src.domain.user.repositories import UserRepository
from application.user.dto import CreateUserDTO, UpdateUserDTO, UserDTO


class UserCommandHandler:
    """
    Command handler for user operations.

    Handles commands that modify user data.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the command handler.

        Args:
            user_repository: Repository for user persistence.
        """
        self.user_repository = user_repository

    def create_user(self, dto: CreateUserDTO) -> UserDTO:
        """
        Create a new user.

        Args:
            dto: The data for creating the user.

        Returns:
            A DTO of the created user.
        """
        user = User(
            username=dto.username,
            name=dto.name,
            email=dto.email,
            password=dto.password,
            is_admin=dto.is_admin
        )
        created_user = self.user_repository.add(user)
        return UserDTO.from_entity(created_user)

    def update_user(self, id: int, dto: UpdateUserDTO) -> Optional[UserDTO]:
        """
        Update an existing user.

        Args:
            id: The ID of the user to update.
            dto: The data for updating the user.

        Returns:
            A DTO of the updated user or None if user not found.
        """
        user = self.user_repository.get_by_id(id)
        if not user:
            return None

        # Update only provided fields
        user_dict = {k: v for k, v in vars(dto).items() if v is not None}
        for key, value in user_dict.items():
            setattr(user, key, value)

        updated_user = self.user_repository.update(user)
        return UserDTO.from_entity(updated_user)

    def delete_user(self, id: int) -> bool:
        """
        Delete a user.

        Args:
            id: The ID of the user to delete.

        Returns:
            True if the user was deleted, False otherwise.
        """
        return self.user_repository.delete(id)