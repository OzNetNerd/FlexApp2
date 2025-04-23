from app.services.relationship_service import RelationshipService

from app.utils.app_logging import get_logger
logger = get_logger()


def get_relationships(entity, entity_type="user"):
    """
    Retrieve and log relationships for a given entity.
    Returns the list of relationships.
    """
    logger.info(f"Adding relationships to the context for {entity.__class__.__name__} {entity.id}.")
    relationships = RelationshipService.get_relationships_for_entity(entity_type, entity.id)
    logger.info(f"Retrieved {len(relationships)} relationships for {entity_type} with ID {entity.id}.")
    logger.debug(f"Payload: {relationships}")
    return relationships
