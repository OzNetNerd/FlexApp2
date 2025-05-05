"""
Base DataLoader classes that implement common loading functionality.

This module provides base classes for implementing DataLoaders in a consistent
and DRY way across the application.
"""

from typing import List, Dict, Optional, TypeVar, Generic, Callable, Type, Any
import strawberry
from dataclasses import dataclass

# Define generic type variables for flexibility
T = TypeVar("T")  # Entity type
K = TypeVar("K")  # Key type (usually int or str)


class BaseLoader(Generic[T, K]):
    """
    Base DataLoader class that implements common batch loading behavior.

    This generic base class handles the common pattern of loading entities
    by their IDs in an efficient batched manner, adhering to DataLoader
    principles.
    """

    def __init__(self, unit_of_work):
        """
        Initialize the DataLoader with a unit of work.

        Args:
            unit_of_work: The UnitOfWork instance for database operations
        """
        self.unit_of_work = unit_of_work

    async def load_by_ids(self, keys: List[K], repository_getter: Callable) -> List[Optional[T]]:
        """
        Load entities by their IDs in a batched operation.

        Args:
            keys: List of entity IDs to load
            repository_getter: Function that returns the appropriate repository
                               from the unit of work

        Returns:
            List[Optional[T]]: List of loaded entities in the same order as the keys,
                               with None for entities that weren't found
        """
        if not keys:
            return []

        with self.unit_of_work:
            repository = repository_getter(self.unit_of_work)
            entities = repository.get_by_ids(keys)

            # Create a mapping of id -> entity for quick lookups
            entities_by_id = {entity.id: entity for entity in entities}

            # Return entities in the same order as the requested keys
            return [entities_by_id.get(key) for key in keys]


@dataclass
class DataLoaderContext:
    """
    Context class that holds all DataLoaders.

    This class provides a single place to store and access all DataLoaders
    needed for resolving GraphQL queries.
    """

    company_loader: Any
    customer_loader: Any
    opportunity_loader: Any
