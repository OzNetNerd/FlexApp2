import logging
from app.services.relationship_service import RelationshipService

logger = logging.getLogger(__name__)


def get_relationships(item, entity_type="user"):
    """
    Retrieve and log relationships for a given item.
    Returns the list of relationships.
    """
    logger.info(f"Adding relationships to the context for {item.__class__.__name__} {item.id}.")
    relationships = RelationshipService.get_relationships_for_entity(entity_type, item.id)
    logger.info(f"Retrieved {len(relationships)} relationships for {entity_type} with ID {item.id}.")
    logger.debug(f"Payload: {relationships}")
    return relationships
