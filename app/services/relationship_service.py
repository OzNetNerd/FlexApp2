# app/services/relationship_service.py

from typing import List, Tuple, Dict, Any, Optional
from app.models.base import db
from app.models.relationship import Relationship
from app.models.user import User
from app.models.contact import Contact
from app.models.company import Company

from app.utils.app_logging import get_logger
logger = get_logger()


class RelationshipService:
    """Service class to manage entity relationships."""

    ENTITY_MODELS = {"user": User, "contact": Contact, "company": Company}

    RELATIONSHIP_TYPES = {
        "user-user": ["Manager", "Colleague", "Direct Report", "Mentor"],
        "user-contact": ["Primary", "Secondary", "Support"],
        "user-company": ["Account Manager", "Sales Lead", "Support Lead"],
        "contact-company": ["Employee", "Executive", "Owner", "Board Member"],
        "company-company": ["Partner", "Supplier", "Customer", "Competitor"],
    }

    @classmethod
    def get_entity(cls, entity_type: str, entity_id: int) -> Any:
        """Get an entity by type and ID."""
        model = cls.ENTITY_MODELS.get(entity_type.lower())
        if not model:
            logger.error(f"❌  Unknown entity type: {entity_type}")
            return None

        return model.query.get(entity_id)

    @classmethod
    def get_relationship_types(cls, entity1_type: str, entity2_type: str) -> List[str]:
        """Get valid relationship types for two entity types."""
        key = f"{entity1_type.lower()}-{entity2_type.lower()}"
        reverse_key = f"{entity2_type.lower()}-{entity1_type.lower()}"

        if key in cls.RELATIONSHIP_TYPES:
            return cls.RELATIONSHIP_TYPES[key]
        elif reverse_key in cls.RELATIONSHIP_TYPES:
            return cls.RELATIONSHIP_TYPES[reverse_key]
        else:
            return []

    @classmethod
    def create_relationship(
        cls, entity1_type: str, entity1_id: int, entity2_type: str, entity2_id: int, relationship_type: str
    ) -> Tuple[bool, Optional[Relationship], str]:
        """Create a relationship between two entities."""
        # Validate entities exist
        entity1 = cls.get_entity(entity1_type, entity1_id)
        if not entity1:
            return False, None, f"{entity1_type.capitalize()} with ID {entity1_id} not found"

        entity2 = cls.get_entity(entity2_type, entity2_id)
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

    @classmethod
    def delete_relationship(cls, relationship_id: int) -> Tuple[bool, str]:
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

    @classmethod
    def get_relationships_for_entity(cls, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """Get all relationships for an entity with related data."""
        relationships = Relationship.query.filter(
            db.or_(
                db.and_(Relationship.entity1_type == entity_type.lower(), Relationship.entity1_id == entity_id),
                db.and_(Relationship.entity2_type == entity_type.lower(), Relationship.entity2_id == entity_id),
            )
        ).all()

        result = []
        for rel in relationships:
            # Get related entity type and id
            if rel.entity1_type == entity_type.lower() and rel.entity1_id == entity_id:
                related_type = rel.entity2_type
                related_id = rel.entity2_id
            else:
                related_type = rel.entity1_type
                related_id = rel.entity1_id

            # Get related entity object
            related_entity = cls.get_entity(related_type, related_id)
            if not related_entity:
                continue

            display_name = getattr(related_entity, "name", str(related_entity))

            result.append(
                {
                    "id": rel.id,
                    "entity_type": related_type,
                    "entity_id": related_id,
                    "entity_name": display_name,
                    "relationship_type": rel.relationship_type,
                }
            )

        return result
