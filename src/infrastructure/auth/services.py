# src/infrastructure/auth/services.py
from flask_login import current_user
from src.domain.user.entities import User
from src.domain.user.repositories import UserRepository


def get_current_user() -> User:
    """
    Retrieves the currently authenticated user.

    Returns:
        User: The current authenticated user entity

    Raises:
        UnauthorizedError: If no user is authenticated
    """
    if not current_user or not current_user.is_authenticated:
        raise UnauthorizedError("No authenticated user found")

    # If current_user is already a domain entity, return it directly
    if isinstance(current_user, User):
        return current_user

    # Otherwise, fetch the full user entity from the repository
    user_repository = UserRepository()
    return user_repository.find_by_id(current_user.id)