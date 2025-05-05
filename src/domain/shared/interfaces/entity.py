"""
Base entity interface for the domain layer.

Defines core functionality for all domain entities.
"""
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID, uuid4


@dataclass
class Entity(ABC):
    """
    Base class for all domain entities.

    Provides common functionality and identity for domain objects.
    Domain entities are distinguished by their identity rather than their attributes.

    Attributes:
        id: The unique identifier of the entity.
    """
    id: UUID = field(default_factory=uuid4)

    def __eq__(self, other: Any) -> bool:
        """
        Equality check based on entity identity.

        Args:
            other: The object to compare with.

        Returns:
            True if the two entities have the same identity, False otherwise.
        """
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """
        Hash based on entity identity.

        Returns:
            Hash value based on entity ID.
        """
        return hash(self.id)