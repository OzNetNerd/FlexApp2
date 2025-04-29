from flask import Blueprint, request

from app.models import Relationship
from app.routes.api.route_registration import ApiCrudRouteConfig
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger
from .json_utils import json_endpoint

logger = get_logger()

ENTITY_NAME = "Relationship"
ENTITY_PLURAL_NAME = "Relationships"

relationships_api_bp = Blueprint(
    f"{ENTITY_NAME.lower()}_api",
    __name__,
    url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}"
)

relationship_service = CRUDService(Relationship)

# Configure standard CRUD routes
relationship_api_crud_config = ApiCrudRouteConfig(
    blueprint=relationships_api_bp,
    entity_table_name=ENTITY_NAME,
    service=relationship_service
)


# Add flexible search endpoint that can replace all specialized queries
@relationships_api_bp.route("/search", methods=["GET"])
@json_endpoint
def search_relationships():
    """
    Search for relationships based on query parameters.

    Query parameters:
    - entity_type: Type of the entity (e.g., 'user', 'contact', 'opportunity')
    - entity_id: ID of the entity
    - related_entity_type: Type of the related entity to filter by
    - relationship_type: Type of relationship to filter by
    """
    entity_type = request.args.get("entity_type")
    entity_id = request.args.get("entity_id")
    related_entity_type = request.args.get("related_entity_type")
    relationship_type = request.args.get("relationship_type")

    if not entity_type or not entity_id:
        return {"success": False, "message": "entity_type and entity_id are required parameters"}, 400

    try:
        entity_id = int(entity_id)
        relationships = Relationship.get_relationships(
            entity_type=entity_type,
            entity_id=entity_id,
            related_entity_type=related_entity_type
        )

        # Filter by relationship_type if provided
        if relationship_type:
            relationships = [r for r in relationships if r.relationship_type == relationship_type]

        # Format the relationships in a consistent way
        formatted_relationships = []
        for relationship in relationships:
            related_type, related_id = relationship.get_related_entity(entity_type, entity_id)
            formatted_relationships.append({
                "id": relationship.id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "related_entity_type": related_type,
                "related_entity_id": related_id,
                "relationship_type": relationship.relationship_type
            })

        return {"success": True, "data": formatted_relationships}

    except ValueError:
        return {"success": False, "message": "entity_id must be an integer"}, 400
    except Exception as e:
        logger.error(f"Error searching relationships: {str(e)}")
        return {"success": False, "message": f"An error occurred: {str(e)}"}, 500