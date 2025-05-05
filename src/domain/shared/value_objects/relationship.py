"""
Value objects for representing relationships between entities.

These value objects capture the semantics of connections between domain entities.
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional
from uuid import UUID


class RelationshipType(Enum):
    """
    Enumeration of possible relationship types between entities.
    """
    EMPLOYEE = auto()
    MANAGER = auto()
    CUSTOMER = auto()
    PARTNER = auto()
    SUPPLIER = auto()
    COMPETITOR = auto()
    OTHER = auto()

    @classmethod
    def from_string(cls, value: str) -> 'RelationshipType':
        """
        Converts a string to a RelationshipType.

        Args:
            value: String representation of the relationship type.

        Returns:
            The corresponding RelationshipType.

        Raises:
            ValueError: If the string doesn't match any RelationshipType.
        """
        try:
            return cls[value.upper()]
        except KeyError:
            return cls.OTHER


@dataclass(frozen=True)
class EntityReference:
    """
    Reference to an entity by its type and ID.

    Attributes:
        entity_type: The type of the entity.
        entity_id: The unique identifier of the entity.
    """
    entity_type: str
    entity_id: UUID

    def __str__(self) -> str:
        return f"{self.entity_type}:{self.entity_id}"


@dataclass(frozen=True)
class Relationship:
    """
    Represents a relationship between two entities.

    Attributes:
        entity1: Reference to the first entity.
        entity2: Reference to the second entity.
        relationship_type: The type of relationship.
    """
    entity1: EntityReference
    entity2: EntityReference
    relationship_type: Optional[RelationshipType] = None

    def __str__(self) -> str:
        relationship = self.relationship_type.name if self.relationship_type else "-"
        return f"{self.entity1} {relationship} {self.entity2}"

    def involves_entity(self, entity_type: str, entity_id: UUID) -> bool:
        """
        Checks if a specific entity is part of this relationship.

        Args:
            entity_type: The type of the entity.
            entity_id: The unique identifier of the entity.

        Returns:
            True if the entity is part of the relationship, False otherwise.
        """
        entity = EntityReference(entity_type, entity_id)
        return self.entity1 == entity or self.entity2 == entity

    def get_related_entity(self, entity_type: str, entity_id: UUID) -> Optional[EntityReference]:
        """
        Gets the entity on the other side of the relationship.

        Args:
            entity_type: The type of the entity.
            entity_id: The unique identifier of the entity.

        Returns:
            The related entity if the provided entity is part of the relationship,
            None otherwise.
        """
        entity = EntityReference(entity_type, entity_id)
        if self.entity1 == entity:
            return self.entity2
        if self.entity2 == entity:
            return self.entity1
        return None