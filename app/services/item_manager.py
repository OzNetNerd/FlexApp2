# import logging
# import traceback
# from flask import flash, redirect, url_for
# from typing import Tuple, Any, Optional
# from sqlalchemy.orm import joinedload, class_mapper, RelationshipProperty
# from app.models.base import db  # Updated import
# from app.services.relationship_service import RelationshipService  # Import the relationship service
#
# logger = logging.getLogger(__name__)
#
#
# class ItemManager:
#     """Handles CRUD operations for model items in web routes."""
#
#     def __init__(self, model, service, blueprint_name):
#         """
#         Initialize the ItemManager.
#
#         Args:
#             model: SQLAlchemy model class.
#             service: CRUD service instance.
#             blueprint_name: Name of the blueprint for route redirection.
#         """
#         self.model = model
#         self.service = service
#         self.blueprint_name = blueprint_name
#
#     def get_item_by_id(self, entity_id) -> Tuple[Optional[Any], Optional[str]]:
#         """
#         Fetch an item by ID with eager loading for supported relationships.
#
#         Args:
#             entity_id: The primary key of the item.
#
#         Returns:
#             Tuple containing the item (or None) and an error message (or None).
#         """
#         try:
#             query = self.model.query
#             mapper = class_mapper(self.model)
#
#             # Handle standard database relationships with eager loading
#             for rel in ("users", "company", "notes", "relationships"):
#                 if hasattr(self.model, rel):
#                     prop = mapper.get_property(rel)
#                     if isinstance(prop, RelationshipProperty) and prop.lazy != "dynamic":
#                         query = query.options(joinedload(getattr(self.model, rel)))
#
#             item = query.filter_by(id=entity_id).first()
#
#             if not item:
#                 return None, f"{self.model.__name__} not found"
#
#             # Special handling for User model to retrieve all relationships
#             if self.model.__name__ == "User":
#                 from app.models.relationship import Relationship
#
#                 # Load relationships where this user is entity1
#                 entity1_relationships = Relationship.query.filter_by(entity1_type="user", entity1_id=entity_id).all()
#
#                 # Load relationships where this user is entity2
#                 entity2_relationships = Relationship.query.filter_by(entity2_type="user", entity2_id=entity_id).all()
#
#                 # Combine all relationships
#                 item.all_relationships = entity1_relationships + entity2_relationships
#
#             logger.info(f"Item found with id {entity_id}")
#             return item, None
#
#         except Exception as e:
#             error_msg = f"Error accessing {self.model.__name__} with id {entity_id}: {str(e)}"
#             logger.error(error_msg)
#             logger.error(f"❌  Traceback: {traceback.format_exc()}")
#             return None, error_msg
#
#     def create_item(self, form_data):
#         """
#         Create a new item from form data.
#
#         Args:
#             form_data: Dictionary of form values.
#
#         Returns:
#             Tuple containing a redirect response (or None) and an error message (or None).
#         """
#         try:
#             logger.info(f"Creating new {self.model.__name__} with data: {list(form_data.keys())}")
#             item = self.service.create(form_data)
#             logger.info(f"{self.model.__name__} created successfully with id {item.id}")
#             flash(f"{self.model.__name__} created successfully", "success")
#             return redirect(url_for(f"{self.blueprint_name}.index")), None
#         except ValueError as ve:
#             logger.warning(f"Validation error during create: {ve}")
#             return None, str(ve)
#         except Exception as e:
#             logger.error(f"❌  Error creating {self.model.__name__}: {e}")
#             logger.error(traceback.format_exc())
#             return None, f"Error creating {self.model.__name__}: {str(e)}"
#
#     def update_item(self, item, form_data):
#         """
#         Update an existing item with form data.
#
#         Args:
#             item: The SQLAlchemy model instance to update.
#             form_data: Dictionary of updated form values.
#
#         Returns:
#             Tuple containing a redirect response (or None) and an error message (or None).
#         """
#         try:
#             logger.info(f"Updating {self.model.__name__} with id {item.id}, fields: {list(form_data.keys())}")
#
#             # Handle relationships separately from regular attributes
#             relationship_fields = ["users", "companies"]
#             relationship_data = {}
#
#             # Extract relationship data and remove from form_data so we don't try to set it directly
#             for field in relationship_fields:
#                 if field in form_data:
#                     relationship_data[field] = form_data[field]
#
#             # Update standard fields first
#             for field, value in form_data.items():
#                 if field not in relationship_fields and hasattr(item, field):
#                     setattr(item, field, value)
#
#             # Update the timestamp for this change
#             if hasattr(item, "updated_at"):
#                 from datetime import datetime
#
#                 item.updated_at = datetime.now()
#
#             # Save the basic changes
#             db.session.commit()
#
#             # Now handle relationships using the RelationshipService if this is a User model
#             if self.model.__name__ == "User" and hasattr(item, "relationships"):
#                 # First clear existing relationships that will be replaced
#                 self._update_user_relationships(item, relationship_data)
#
#             # Final commit for all changes
#             db.session.commit()
#
#             logger.info(f"{self.model.__name__} with id {item.id} updated successfully")
#             flash(f"{self.model.__name__} updated successfully", "success")
#             return redirect(url_for(f"{self.blueprint_name}.view", entity_id=item.id)), None
#
#         except ValueError as ve:
#             logger.warning(f"Validation error during update: {ve}")
#             return None, str(ve)
#         except Exception as e:
#             logger.error(f"❌  Error updating {self.model.__name__} with id {item.id}: {e}")
#             logger.error(traceback.format_exc())
#             db.session.rollback()
#             return None, f"Error updating {self.model.__name__}: {str(e)}"
#
#     def _update_user_relationships(self, user, relationship_data):
#         """
#         Update relationships for a user using RelationshipService.
#
#         Args:
#             user: User model instance to update relationships for
#             relationship_data: Dictionary containing relationship ids
#         """
#         # First, clear existing relationships we're going to replace
#         # This is a simplified approach - a more advanced solution would
#         # only remove relationships that are no longer needed
#         from app.models.relationship import Relationship
#
#         # Process user relationships
#         if "users" in relationship_data and relationship_data["users"]:
#             # Clear existing user-user relationships
#             existing_relationships = Relationship.query.filter(
#                 ((Relationship.entity1_type == "user") & (Relationship.entity1_id == user.id) & (Relationship.entity2_type == "user"))
#                 | ((Relationship.entity2_type == "user") & (Relationship.entity2_id == user.id) & (Relationship.entity1_type == "user"))
#             ).all()
#
#             for rel in existing_relationships:
#                 db.session.delete(rel)
#             db.session.flush()  # Flush to database but don't commit yet
#
#             # Create new relationships
#             for related_user_id in relationship_data["users"]:
#                 if str(related_user_id) != str(user.id):  # Prevent self-relationship
#                     RelationshipService.create_relationship(
#                         "user", user.id, "user", int(related_user_id), "Colleague"  # Default relationship type - could be made configurable
#                     )
#
#         # Process company relationships
#         if "companies" in relationship_data and relationship_data["companies"]:
#             # Clear existing user-company relationships
#             existing_relationships = Relationship.query.filter(
#                 ((Relationship.entity1_type == "user") & (Relationship.entity1_id == user.id) & (Relationship.entity2_type == "company"))
#                 | ((Relationship.entity2_type == "company") & (Relationship.entity2_id == user.id) & (Relationship.entity1_type == "user"))
#             ).all()
#
#             for rel in existing_relationships:
#                 db.session.delete(rel)
#             db.session.flush()  # Flush to database but don't commit yet
#
#             # Create new relationships
#             for company_id in relationship_data["companies"]:
#                 RelationshipService.create_relationship(
#                     "user", user.id, "company", int(company_id), "Account Manager"  # Default relationship type - could be made configurable
#                 )
#
#     def delete_item(self, item):
#         """
#         Delete an existing item.
#
#         Args:
#             item: The SQLAlchemy model instance to delete.
#
#         Returns:
#             Tuple of (True/False if deleted, error message or None).
#         """
#         try:
#             self.service.delete(item)
#             logger.info(f"{self.model.__name__} with id {item.id} deleted successfully")
#             flash(f"{self.model.__name__} deleted successfully", "success")
#             return True, None
#         except Exception as e:
#             logger.error(f"❌  Error deleting {self.model.__name__} with id {item.id}: {str(e)}")
#             logger.error(f"❌  Traceback: {traceback.format_exc()}")
#             return False, f"❌  Error deleting {self.model.__name__}: {str(e)}"
