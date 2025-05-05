"""DataLoader for User entities."""

from typing import List, Dict, Any
from .base import BaseDataLoader
from src.domain.user.repositories import UserRepository
from src.infrastructure.persistence.repositories.user_repository import SQLAlchemyUserRepository


class UserDataLoader(BaseDataLoader):
    """DataLoader for User entities."""

    def __init__(self):
        """Initialize with repository."""
        super().__init__()
        self.repository: UserRepository = SQLAlchemyUserRepository()

    async def batch_load_fn(self, keys: List[int]) -> List[Dict[str, Any]]:
        """
        Load users in batch by IDs.

        Args:
            keys: List of user IDs to load

        Returns:
            List of user dicts in same order as keys
        """
        entities = [self.repository.get_by_id(key) for key in keys]
        return [
            (
                {
                    "id": entity.id,
                    "username": entity.username,
                    "name": entity.name,
                    "email": entity.email,
                    "is_admin": entity.is_admin,
                    "created_at": entity.created_at,
                    "updated_at": entity.updated_at,
                    "related_users": entity.related_users,
                    "related_companies": entity.related_companies,
                }
                if entity
                else None
            )
            for entity in entities
        ]
