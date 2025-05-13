# app/services/relationship/core.py
from typing import Any, Optional, Tuple

from app.models.base import db
from app.models.relationship import Relationship
from app.services.service_base import ServiceBase
from app.utils.app_logging import get_logger

logger = get_logger()


class RelationshipCoreService(ServiceBase):
    """Core service for relationship management."""

    def __init__(self):
        super().__init__()

    def get_entity(self, entity_type: str, entity_id: int, entity_models: dict) -> Any:
        """Get an entity by type and ID."""
        model = entity_models.get(entity_type.lower())
        if not model:
            logger.error(f"❌  Unknown entity type: {entity_type}")
            return None

        return model.query.get(entity_id)

    def create_relationship(
        self, entity1_type: str, entity1_id: int, entity2_type: str, entity2_id: int, relationship_type: str, entity_models: dict
    ) -> Tuple[bool, Optional[Relationship], str]:
        """Create a relationship between two entities."""
        # Validate entities exist
        entity1 = self.get_entity(entity1_type, entity1_id, entity_models)
        if not entity1:
            return False, None, f"{entity1_type.capitalize()} with ID {entity1_id} not found"

        entity2 = self.get_entity(entity2_type, entity2_id, entity_models)
        if not entity2:
            return False, None, f"{entity2_type.capitalize()} with ID {entity2_id} not found"

        # Check if relationship already exists
        existing = Relationship.query.filter_by(
            entity1_type=entity1_type.lower(),
            entity1_id=entity1_id,
            entity2_type=entity2_type.lower(),
            entity2_id=entity2_id,
            relationship_type=relationship_type,
        ).first()

        if existing:
            return False, None, "This relationship already exists"

        # Create the relationship
        try:
            relationship = Relationship(
                entity1_type=entity1_type.lower(),
                entity1_id=entity1_id,
                entity2_type=entity2_type.lower(),
                entity2_id=entity2_id,
                relationship_type=relationship_type,
            )

            # For backward compatibility
            if entity1_type.lower() == "user" and entity2_type.lower() == "contact":
                relationship.user_id = entity1_id
                relationship.contact_id = entity2_id

            db.session.add(relationship)
            db.session.commit()

            logger.info(f"Created relationship: {entity1_type}={entity1_id} {relationship_type} {entity2_type}={entity2_id}")
            return True, relationship, "Relationship created successfully"

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌  Error creating relationship: {str(e)}")
            return False, None, f"Error creating relationship: {str(e)}"

    def delete_relationship(self, relationship_id: int) -> Tuple[bool, str]:
        """Delete a relationship."""
        try:
            relationship = Relationship.query.get(relationship_id)
            if not relationship:
                return False, "Relationship not found"

            db.session.delete(relationship)
            db.session.commit()

            logger.info(f"Deleted relationship: {relationship_id}")
            return True, "Relationship deleted successfully"

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌  Error deleting relationship: {str(e)}")
            return False, f"❌  Error deleting relationship: {str(e)}"
