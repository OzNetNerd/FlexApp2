# app/services/relationship/query.py
from typing import Any, Dict, List
from sqlalchemy import and_, or_

from app.models.relationship import Relationship
from app.services.service_base import ServiceBase
from app.utils.app_logging import get_logger

logger = get_logger()


class RelationshipQueryService(ServiceBase):
    """Service for relationship queries."""

    def __init__(self):
        super().__init__()

    def get_relationships_for_entity(self, entity_type: str, entity_id: int, entity_models: dict) -> List[
        Dict[str, Any]]:
        """Get all relationships for an entity with related data."""
        relationships = Relationship.query.filter(
            or_(
                and_(Relationship.entity1_type == entity_type.lower(), Relationship.entity1_id == entity_id),
                and_(Relationship.entity2_type == entity_type.lower(), Relationship.entity2_id == entity_id),
            )
        ).all()

        result = []
        for rel in relationships:
            # Determine the related side
            if rel.entity1_type == entity_type.lower() and rel.entity1_id == entity_id:
                related_type = rel.entity2_type
                related_id = rel.entity2_id
            else:
                related_type = rel.entity1_type
                related_id = rel.entity1_id

            model = entity_models.get(related_type)
            if not model:
                continue

            related_entity = model.query.get(related_id)
            if not related_entity:
                continue

            display_name = getattr(related_entity, "name", str(related_entity))

            result.append({
                "id": rel.id,
                "entity_type": related_type,
                "entity_id": related_id,
                "entity_name": display_name,
                "relationship_type": rel.relationship_type,
            })

        return result

    def get_entities_by_type(self, entity_type: str, related_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """Get related entities of a specific type."""
        rels = self.get_relationships_for_entity(entity_type, entity_id, self._get_relationship_service().ENTITY_MODELS)
        return [r for r in rels if r["entity_type"] == related_type]

    def _get_relationship_service(self):
        from app.services import get_service
        return get_service('relationship')