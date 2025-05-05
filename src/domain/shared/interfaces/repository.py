"""
Base repository interface for Domain-Driven Design.

This module defines the generic repository interface that all
domain-specific repositories should implement.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any

# Define a generic type for entities
T = TypeVar('T')


class Repository(Generic[T], ABC):
    """
    Base repository interface for domain entities.

    This interface defines the standard methods that all repositories
    should implement to provide data access for domain entities.
    """

    @abstractmethod
    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Retrieve an entity by its ID.

        Args:
            entity_id: The ID of the entity to retrieve

        Returns:
            Optional[T]: The entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        """
        Retrieve all entities.

        Returns:
            List[T]: All entities in the repository
        """
        pass

    @abstractmethod
    async def add(self, entity: T) -> T:
        """
        Add a new entity to the repository.

        Args:
            entity: The entity to add

        Returns:
            T: The added entity (possibly with updated ID)
        """
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        Update an existing entity in the repository.

        Args:
            entity: The entity to update

        Returns:
            T: The updated entity
        """
        pass

    @abstractmethod
    async def remove(self, entity_id: Any) -> bool:
        """
        Remove an entity from the repository.

        Args:
            entity_id: The ID of the entity to remove

        Returns:
            bool: True if the entity was removed, False otherwise
        """
        pass