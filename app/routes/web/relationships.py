import logging
from flask import Blueprint, request, render_template, flash, redirect, url_for
from app.models import Relationship
from app.routes.web.crud.components.generic_crud_routes import GenericWebRoutes
from app.models.base import db
from app.services.relationship_service import RelationshipService

logger = logging.getLogger(__name__)

# Define the blueprint
relationships_bp = Blueprint("relationships_bp", __name__, url_prefix="/relationships")


class RelationshipCRUDRoutes(GenericWebRoutes):
    """
    Enhanced CRUD routes for managing relationships between various entity types.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.register_custom_routes()
#
#     def register_custom_routes(self):
#         """Register custom routes for relationship management."""
#         bp = self.blueprint
#
#         @bp.route("/add/<entity_type>/<int:entity_id>", methods=["GET", "POST"])
#         def add_relationship(entity_type, entity_id):
#             """Add a relationship for an entity."""
#             entity = RelationshipService.get_entity(entity_type, entity_id)
#             if not entity:
#                 flash(f"{entity_type.capitalize()} not found", "error")
#                 return redirect(url_for("main.index"))
#
#             if request.method == "POST":
#                 related_entity_type = request.form.get("related_entity_type")
#                 related_entity_id = request.form.get("related_entity_id")
#                 relationship_type = request.form.get("relationship_type")
#
#                 if not related_entity_type or not related_entity_id or not relationship_type:
#                     flash("All fields are required", "error")
#                     return redirect(request.url)
#
#                 success, relationship, message = RelationshipService.create_relationship(
#                     entity_type,
#                     entity_id,
#                     related_entity_type,
#                     int(related_entity_id),
#                     relationship_type,
#                 )
#
#                 flash(message, "success" if success else "error")
#
#                 # Redirect to view page for entity
#                 if entity_type == "user":
#                     return redirect(url_for("users.view", item_id=entity_id))
#                 elif entity_type == "contact":
#                     return redirect(url_for("contacts.view", item_id=entity_id))
#                 elif entity_type == "company":
#                     return redirect(url_for("companies.view", item_id=entity_id))
#                 else:
#                     return redirect(url_for("main.index"))
#
#             entity_types = [
#                 {"value": "user", "label": "User"},
#                 {"value": "contact", "label": "Contact"},
#                 {"value": "company", "label": "Company"},
#             ]
#             relationship_types = []
#
#             return render_template(
#                 "relationship/add.html",
#                 entity=entity,
#                 entity_type=entity_type,
#                 entity_id=entity_id,
#                 entity_types=entity_types,
#                 relationship_types=relationship_types,
#             )
#
#         @bp.route("/delete/<int:relationship_id>", methods=["POST"])
#         def delete_relationship(relationship_id):
#             """Delete a relationship."""
#             relationship = Relationship.query.get_or_404(relationship_id)
#
#             source_type = request.args.get("source_type") or relationship.entity1_type
#             source_id = request.args.get("source_id") or relationship.entity1_id
#
#             success, message = RelationshipService.delete_relationship(relationship_id)
#
#             flash(message, "success" if success else "error")
#
#             if source_type == "user":
#                 return redirect(url_for("users.view", item_id=source_id))
#             elif source_type == "contact":
#                 return redirect(url_for("contacts.view", item_id=source_id))
#             elif source_type == "company":
#                 return redirect(url_for("companies.view", item_id=source_id))
#             else:
#                 return redirect(url_for("main.index"))
#
#         @bp.route("/api/get_entities/<entity_type>", methods=["GET"])
#         def get_entities(entity_type):
#             """API endpoint to get entities of a specific type."""
#             exclude_id = request.args.get("exclude_id")
#
#             model = RelationshipService.ENTITY_MODELS.get(entity_type.lower())
#             if not model:
#                 return {"success": False, "entities": []}
#
#             query = model.query
#             if exclude_id:
#                 query = query.filter(model.id != exclude_id)
#
#             entities = query.all()
#
#             result = [{"id": e.id, "name": getattr(e, "name", str(e))} for e in entities]
#
#             return {"success": True, "entities": result}
#
#         @bp.route("/api/get_relationship_types", methods=["GET"])
#         def get_relationship_types():
#             """API endpoint to get relationship types for a pair of entity types."""
#             entity1_type = request.args.get("entity1_type")
#             entity2_type = request.args.get("entity2_type")
#
#             if not entity1_type or not entity2_type:
#                 return {"success": False, "types": []}
#
#             types = RelationshipService.get_relationship_types(entity1_type, entity2_type)
#
#             return {"success": True, "types": types}
#
#
# Register CRUD route handler
relationship_routes = RelationshipCRUDRoutes(
    blueprint=relationships_bp,
    model=Relationship,
    required_fields=["entity1_type", "entity1_id", "entity2_type", "entity2_id"],
    unique_fields=["entity1_type", "entity1_id", "entity2_type", "entity2_id", "relationship_type"],
    index_template="relationships.html",
)

# logger.info("Successfully set up 'Relationship CRUD' routes.")
