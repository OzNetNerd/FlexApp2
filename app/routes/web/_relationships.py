# # app/routes/web/relationship.py
#
# import logging
# from app.models import Relationship
# from app.routes.web import relationships_bp
# from app.routes.web.generic_crud_routes import GenericWebRoutes
# from flask import request, render_template, flash, redirect, url_for
# from app.models.base import db
# from app.services.relationship_service import RelationshipService
#
# logger = logging.getLogger(__name__)
#
#
# class RelationshipCRUDRoutes(GenericWebRoutes):
#     """
#     Enhanced CRUD routes for managing relationships between various entity types.
#     """
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         # Register additional routes
#         self.register_custom_routes()
#
#     def register_custom_routes(self):
#         """Register custom routes for relationship management."""
#         bp = self.blueprint
#
#         @bp.route('/add/<entity_type>/<int:entity_id>', methods=['GET', 'POST'])
#         def add_relationship(entity_type, entity_id):
#             """Add a relationship for an entity."""
#             # Get the entity
#             entity = RelationshipService.get_entity(entity_type, entity_id)
#             if not entity:
#                 flash(f"{entity_type.capitalize()} not found", "error")
#                 return redirect(url_for('main.index'))
#
#             if request.method == 'POST':
#                 related_entity_type = request.form.get('related_entity_type')
#                 related_entity_id = request.form.get('related_entity_id')
#                 relationship_type = request.form.get('relationship_type')
#
#                 # Validate form data
#                 if not related_entity_type or not related_entity_id or not relationship_type:
#                     flash("All fields are required", "error")
#                     return redirect(request.url)
#
#                 # Create the relationship
#                 success, relationship, message = RelationshipService.create_relationship(
#                     entity_type, entity_id,
#                     related_entity_type, int(related_entity_id),
#                     relationship_type
#                 )
#
#                 flash(message, "success" if success else "error")
#
#                 # Redirect to appropriate view page based on entity type
#                 if entity_type == 'user':
#                     return redirect(url_for('users.view', id=entity_id))
#                 elif entity_type == 'contact':
#                     return redirect(url_for('contacts.view', id=entity_id))
#                 elif entity_type == 'company':
#                     return redirect(url_for('companies.view', id=entity_id))
#                 else:
#                     return redirect(url_for('main.index'))
#
#             # GET request - prepare form data
#             # Get available entity types to relate to
#             entity_types = [
#                 {'value': 'user', 'label': 'User'},
#                 {'value': 'contact', 'label': 'Contact'},
#                 {'value': 'company', 'label': 'Company'}
#             ]
#
#             # Initial relationship types (will be updated via JS)
#             relationship_types = []
#
#             return render_template(
#                 'relationship/add.html',
#                 entity=entity,
#                 entity_type=entity_type,
#                 entity_id=entity_id,
#                 entity_types=entity_types,
#                 relationship_types=relationship_types
#             )
#
#         @bp.route('/delete/<int:relationship_id>', methods=['POST'])
#         def delete_relationship(relationship_id):
#             """Delete a relationship."""
#             # Get the relationship
#             relationship = Relationship.query.get_or_404(relationship_id)
#
#             # Get source entity info for redirect after deletion
#             if request.args.get('source_type') and request.args.get('source_id'):
#                 source_type = request.args.get('source_type')
#                 source_id = request.args.get('source_id')
#             else:
#                 # Default to first entity in the relationship
#                 source_type = relationship.entity1_type
#                 source_id = relationship.entity1_id
#
#             # Delete the relationship
#             success, message = RelationshipService.delete_relationship(relationship_id)
#
#             flash(message, "success" if success else "error")
#
#             # Redirect to appropriate view page based on entity type
#             if source_type == 'user':
#                 return redirect(url_for('users.view', id=source_id))
#             elif source_type == 'contact':
#                 return redirect(url_for('contacts.view', id=source_id))
#             elif source_type == 'company':
#                 return redirect(url_for('companies.view', id=source_id))
#             else:
#                 return redirect(url_for('main.index'))
#
#         @bp.route('/api/get_entities/<entity_type>', methods=['GET'])
#         def get_entities(entity_type):
#             """API endpoint to get entities of a specific type."""
#             exclude_id = request.args.get('exclude_id')
#
#             model = RelationshipService.ENTITY_MODELS.get(entity_type.lower())
#             if not model:
#                 return {'success': False, 'entities': []}
#
#             query = model.query
#             if exclude_id:
#                 query = query.filter(model.id != exclude_id)
#
#             entities = query.all()
#
#             result = [
#                 {
#                     'id': entity.id,
#                     'name': getattr(entity, 'name', str(entity))
#                 }
#                 for entity in entities
#             ]
#
#             return {'success': True, 'entities': result}
#
#         @bp.route('/api/get_relationship_types', methods=['GET'])
#         def get_relationship_types():
#             """API endpoint to get relationship types for a pair of entity types."""
#             entity1_type = request.args.get('entity1_type')
#             entity2_type = request.args.get('entity2_type')
#
#             if not entity1_type or not entity2_type:
#                 return {'success': False, 'types': []}
#
#             types = RelationshipService.get_relationship_types(entity1_type, entity2_type)
#
#             return {'success': True, 'types': types}
#
#
# # Set up the CRUD routes for relationships
# relationship_routes = RelationshipCRUDRoutes(
#     blueprint=relationships_bp,
#     model=Relationship,
#     required_fields=["entity1_type", "entity1_id", "entity2_type", "entity2_id"],
#     unique_fields=["entity1_type", "entity1_id", "entity2_type", "entity2_id", "relationship_type"],
#     index_template="relationships.html",
# )
#
# logger.info("Relationship CRUD routes setup successfully.")
