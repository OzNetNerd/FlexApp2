import logging
import traceback
from flask import flash, redirect, url_for
from typing import Tuple, Any, Optional

logger = logging.getLogger(__name__)


class ItemManager:
    """Handles CRUD operations for model items."""

    def __init__(self, model, service, blueprint_name):
        self.model = model
        self.service = service
        self.blueprint_name = blueprint_name

    def get_item_by_id(self, item_id) -> Tuple[Optional[Any], Optional[str]]:
        """Fetch an item by ID with error handling."""
        try:
            item = self.service.get_by_id(self.model, item_id)
            logger.debug(f"Item found with id {item_id}")
            return item, None
        except Exception as e:
            error_msg = f"Error accessing {self.model.__name__} with id {item_id}: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None, error_msg

    def create_item(self, form_data):
        """Create a new item from form data."""
        try:
            logger.debug(f"Creating new {self.model.__name__} with data: {list(form_data.keys())}")
            item = self.service.create(form_data)
            logger.info(f"{self.model.__name__} created successfully with id {item.id}")
            flash(f'{self.model.__name__} created successfully', 'success')
            return redirect(url_for(f'{self.blueprint_name}.index')), None
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None, f'Error creating {self.model.__name__}: {str(e)}'

    def update_item(self, item, form_data):
        """Update an existing item with form data."""
        try:
            logger.debug(f"Updating {self.model.__name__} with id {item.id}, fields: {list(form_data.keys())}")
            self.service.update(item, form_data)
            logger.info(f"{self.model.__name__} with id {item.id} updated successfully")
            flash(f'{self.model.__name__} updated successfully', 'success')
            return redirect(url_for(f'{self.blueprint_name}.view', item_id=item.id)), None
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__} with id {item.id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None, f'Error updating {self.model.__name__}: {str(e)}'

    def delete_item(self, item):
        """Delete an existing item."""
        try:
            self.service.delete(item)
            logger.info(f"{self.model.__name__} with id {item.id} deleted successfully")
            flash(f'{self.model.__name__} deleted successfully', 'success')
            return True, None
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} with id {item.id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False, f'Error deleting {self.model.__name__}: {str(e)}'