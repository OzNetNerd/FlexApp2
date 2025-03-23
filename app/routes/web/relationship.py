import logging
from app.models import Relationship
from app.routes.web import relationships_bp
from app.routes.web.generic import GenericWebRoutes

logger = logging.getLogger(__name__)


class RelationshipCRUDRoutes(GenericWebRoutes):
    """
    CRUD routes for managing relationships between users and contacts.
    """


relationship_routes = RelationshipCRUDRoutes(
    blueprint=relationships_bp,
    model=Relationship,
    required_fields=["user_id", "contact_id"],
    unique_fields=["user_id", "contact_id"],  # One relationship per user-contact pair
    index_template="relationships.html",
)
