"""Data Transfer Objects for user operations."""

from typing import Optional
from dataclasses import dataclass


@dataclass
class UserDTO:
    """
    User Data Transfer Object for application layer operations.

    Attributes:
        id: The unique identifier for the user.
        username: The unique username for authentication.
        name: The display name of the user.
        email: The user's email address.
        is_admin: Whether the user has administrative privileges.
    """
    id: Optional[int] = None
    username: str = ""
    name: str = ""
    email: str = ""
    is_admin: bool = False

    @classmethod
    def from_entity(cls, user) -> 'UserDTO':
        """
        Create a DTO from a user entity.

        Args:
            user: The user entity to convert.

        Returns:
            A UserDTO containing the entity data.
        """
        return cls(
            id=user.id,
            username=user.username,
            name=user.name,
            email=user.email,
            is_admin=user.is_admin
        )


@dataclass
class CreateUserDTO:
    """
    DTO for user creation operations.

    Attributes:
        username: The unique username for authentication.
        name: The display name of the user.
        email: The user's email address.
        password: The password for authentication.
        is_admin: Whether the user has administrative privileges.
    """
    username: str
    name: str
    email: str
    password: str
    is_admin: bool = False


@dataclass
class UpdateUserDTO:
    """
    DTO for user update operations.

    Attributes:
        username: The unique username for authentication.
        name: The display name of the user.
        email: The user's email address.
        password: The password for authentication.
        is_admin: Whether the user has administrative privileges.
    """
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None