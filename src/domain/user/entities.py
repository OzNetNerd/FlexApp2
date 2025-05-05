"""User domain entity representing a system user."""

from typing import Optional
from src.domain.shared.interfaces.entity import Entity


class User(Entity):
    """
    User domain entity with authentication and authorization information.

    Attributes:
        id: Unique identifier for the user
        username: Username for authentication
        name: User's full name
        email: User's email address
        is_admin: Whether user has admin privileges
        created_at: Creation timestamp
        updated_at: Last update timestamp
        related_users: JSON string of related users
        related_companies: JSON string of related companies
    """

    def __init__(
        self,
        id: int,
        username: str,
        name: str,
        email: str,
        is_admin: bool = False,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        related_users: Optional[str] = None,
        related_companies: Optional[str] = None,
    ):
        """Initialize a new User instance."""
        self.id = id
        self.username = username
        self.name = name
        self.email = email
        self.is_admin = is_admin
        self.created_at = created_at
        self.updated_at = updated_at
        self.related_users = related_users
        self.related_companies = related_companies
