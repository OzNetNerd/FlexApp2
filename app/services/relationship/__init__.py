# app/services/relationship/__init__.py
from typing import Any, Dict, List, Optional, Tuple

from app.models.pages.company import Company
from app.models.pages.contact import Contact
from app.models.relationship import Relationship
from app.services.service_base import ServiceBase, ServiceRegistry
from app.services.relationship.core import RelationshipCoreService
from app.services.relationship.query import RelationshipQueryService
from app.services.relationship.types import RelationshipTypeService


class RelationshipService(ServiceBase):
    """Service class to manage entity relationships and helper mappings."""

    @property
    def ENTITY_MODELS(self):
        """Lazy-loaded entity models to avoid circular imports."""
        from app.models.pages.user import User

        return {"user": User, "contact": Contact, "company": Company}

    RELATIONSHIP_TYPES = RelationshipTypeService.RELATIONSHIP_TYPES

    def __init__(self):
        """Initialize the Relationship service with sub-services."""
        super().__init__()
        self.core = ServiceRegistry.get(RelationshipCoreService)
        self.query = ServiceRegistry.get(RelationshipQueryService)
        self.types = ServiceRegistry.get(RelationshipTypeService)

    # Core methods
    def get_entity(self, entity_type: str, entity_id: int) -> Any:
        """Get an entity by type and ID."""

        return self.core.get_entity(entity_type, entity_id, self.ENTITY_MODELS)

    def create_relationship(
        self, entity1_type: str, entity1_id: int, entity2_type: str, entity2_id: int, relationship_type: str
    ) -> Tuple[bool, Optional[Relationship], str]:
        """Create a relationship between two entities."""
        return self.core.create_relationship(entity1_type, entity1_id, entity2_type, entity2_id, relationship_type, self.ENTITY_MODELS)

    def delete_relationship(self, relationship_id: int) -> Tuple[bool, str]:
        """Delete a relationship."""
        return self.core.delete_relationship(relationship_id)

    # Type methods
    def get_relationship_types(self, entity1_type: str, entity2_type: str) -> List[str]:
        """Get valid relationship types for two entity types."""
        return self.types.get_relationship_types(entity1_type, entity2_type)

    # Query methods
    def get_relationships_for_entity(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """Get all relationships for an entity with related data."""
        return self.query.get_relationships_for_entity(entity_type, entity_id, self.ENTITY_MODELS)

    # Helper mappings
    def get_user_companies(self, user_id: int) -> List[Dict[str, Any]]:
        """Fetch companies related to a user."""
        return self.query.get_entities_by_type("user", "company", user_id)

    def get_user_opportunities(self, user_id: int) -> List[Dict[str, Any]]:
        """Fetch opportunities related to a user."""
        return self.query.get_entities_by_type("user", "opportunity", user_id)

    def get_user_contacts(self, user_id: int) -> List[Dict[str, Any]]:
        """Fetch contacts related to a user."""
        return self.query.get_entities_by_type("user", "contact", user_id)

    def get_contact_contacts(self, contact_id: int) -> List[Dict[str, Any]]:
        """Fetch contacts related to a contact."""
        return self.query.get_entities_by_type("contact", "contact", contact_id)

    def get_contact_opportunities(self, contact_id: int) -> List[Dict[str, Any]]:
        """Fetch opportunities related to a contact."""
        return self.query.get_entities_by_type("contact", "opportunity", contact_id)

    def get_opportunity_companies(self, opportunity_id: int) -> List[Dict[str, Any]]:
        """Fetch companies related to an opportunity."""
        return self.query.get_entities_by_type("opportunity", "company", opportunity_id)
