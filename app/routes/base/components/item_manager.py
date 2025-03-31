import logging
import traceback
from flask import flash, redirect, url_for
from typing import Tuple, Any, Optional
from sqlalchemy.orm import joinedload, class_mapper, RelationshipProperty
from app.models.base import db  # Updated import

logger = logging.getLogger(__name__)


class ItemManager:
    """Handles CRUD operations for model items in web routes."""

    def __init__(self, model, service, blueprint_name):
        """
        Initialize the ItemManager.

        Args:
            model: SQLAlchemy model class.
            service: CRUD service instance.
            blueprint_name: Name of the blueprint for route redirection.
        """
        self.model = model
        self.service = service
        self.blueprint_name = blueprint_name

    def get_item_by_id(self, item_id) -> Tuple[Optional[Any], Optional[str]]:
        """
        Fetch an item by ID with eager loading for supported relationships.

        Args:
            item_id: The primary key of the item.

        Returns:
            Tuple containing the item (or None) and an error message (or None).
        """
        try:
            query = self.model.query
            mapper = class_mapper(self.model)

            for rel in ("users", "company", "notes", "relationships"):
                if hasattr(self.model, rel):
                    prop = mapper.get_property(rel)
                    if isinstance(prop, RelationshipProperty) and prop.lazy != "dynamic":
                        query = query.options(joinedload(getattr(self.model, rel)))

            item = query.filter_by(id=item_id).first()

            if not item:
                return None, f"{self.model.__name__} not found"

            logger.debug(f"Item found with id {item_id}")
            return item, None

        except Exception as e:
            error_msg = f"Error accessing {self.model.__name__} with id {item_id}: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None, error_msg

    def create_item(self, form_data):
        """
        Create a new item from form data.

        Args:
            form_data: Dictionary of form values.

        Returns:
            Tuple containing a redirect response (or None) and an error message (or None).
        """
        try:
            logger.debug(f"Creating new {self.model.__name__} with data: {list(form_data.keys())}")
            item = self.service.create(form_data)
            logger.info(f"{self.model.__name__} created successfully with id {item.id}")
            flash(f"{self.model.__name__} created successfully", "success")
            return redirect(url_for(f"{self.blueprint_name}.index")), None
        except ValueError as ve:
            logger.warning(f"Validation error during create: {ve}")
            return None, str(ve)
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            logger.error(traceback.format_exc())
            return None, f"Error creating {self.model.__name__}: {str(e)}"

    def update_item(self, item, form_data):
        """
        Update an existing item with form data.

        Args:
            item: The SQLAlchemy model instance to update.
            form_data: Dictionary of updated form values.

        Returns:
            Tuple containing a redirect response (or None) and an error message (or None).
        """
        try:
            logger.debug(f"Updating {self.model.__name__} with id {item.id}, fields: {list(form_data.keys())}")

            # Manually update relationship fields.
            if "users" in form_data:
                from app.models.user import User  # Adjust the import path if needed.
                # Convert list of user ID strings to User model instances.
                item.users = [User.query.get(int(uid)) for uid in form_data["users"] if uid]
            if "companies" in form_data:
                from app.models.company import Company  # Adjust the import path if needed.
                # Convert list of company ID strings to Company model instances.
                item.companies = [Company.query.get(int(cid)) for cid in form_data["companies"] if cid]

            # Update all other fields.
            for field, value in form_data.items():
                if field not in ["users", "companies"]:
                    setattr(item, field, value)

            # Commit changes using the db session.
            db.session.commit()
            logger.info(f"{self.model.__name__} with id {item.id} updated successfully")
            flash(f"{self.model.__name__} updated successfully", "success")
            return redirect(url_for(f"{self.blueprint_name}.view", item_id=item.id)), None
        except ValueError as ve:
            logger.warning(f"Validation error during update: {ve}")
            return None, str(ve)
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__} with id {item.id}: {e}")
            logger.error(traceback.format_exc())
            db.session.rollback()
            return None, f"Error updating {self.model.__name__}: {str(e)}"

    def delete_item(self, item):
        """
        Delete an existing item.

        Args:
            item: The SQLAlchemy model instance to delete.

        Returns:
            Tuple of (True/False if deleted, error message or None).
        """
        try:
            self.service.delete(item)
            logger.info(f"{self.model.__name__} with id {item.id} deleted successfully")
            flash(f"{self.model.__name__} deleted successfully", "success")
            return True, None
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} with id {item.id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False, f"Error deleting {self.model.__name__}: {str(e)}"
