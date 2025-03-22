# Handles core database operations (query, create, update, delete)
# Contains shared validation logic

from typing import List, Dict, Any, Type, Optional
from models.base import db
import logging
import traceback

logger = logging.getLogger(__name__)


class CRUDService:
    """
    Service layer for CRUD operations on database models.
    Separates business logic from presentation concerns.
    """

    @staticmethod
    def get_all(model_class, page=1, per_page=15, sort_column='id', sort_direction='asc', filters=None):
        """
        Get all items with pagination, sorting, and filtering.
        """
        try:
            query = model_class.query

            # Apply filters if they exist
            if filters:
                for col_id, filter_config in filters.items():
                    if hasattr(model_class, col_id):
                        column = getattr(model_class, col_id)
                        filter_type = filter_config.get('type')
                        filter_value = filter_config.get('filter')
                        logger.debug(f"Applying filter on {col_id}: {filter_type}={filter_value}")
                        if filter_type == 'contains':
                            query = query.filter(column.ilike(f'%{filter_value}%'))
                        elif filter_type == 'equals':
                            query = query.filter(column == filter_value)

            # Apply sorting
            if hasattr(model_class, sort_column):
                column = getattr(model_class, sort_column)
                query = query.order_by(column.desc() if sort_direction == 'desc' else column)

            # Apply pagination
            items = query.paginate(page=page, per_page=per_page, error_out=False)

            return items
        except Exception as e:
            logger.error(f"Error in get_all for {model_class.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    @staticmethod
    def get_by_id(model_class, item_id):
        """
        Get a single item by ID.
        """
        try:
            return model_class.query.get_or_404(item_id)
        except Exception as e:
            logger.error(f"Error in get_by_id for {model_class.__name__} with id {item_id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    @staticmethod
    def create(model_class, data):
        """
        Create a new item.
        """
        try:
            # Remove empty strings from data
            data = {k: v for k, v in data.items() if v != ''}

            item = model_class(**data)
            db.session.add(item)
            db.session.commit()
            return item
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating {model_class.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    @staticmethod
    def update(item, data):
        """
        Update an existing item.
        """
        try:
            # Remove empty strings from data
            data = {k: v for k, v in data.items() if v != ''}

            for key, value in data.items():
                if hasattr(item, key):
                    setattr(item, key, value)

            db.session.commit()
            return item
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating {item.__class__.__name__} with id {item.id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    @staticmethod
    def delete(item):
        """
        Delete an item.
        """
        try:
            db.session.delete(item)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting {item.__class__.__name__} with id {item.id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    @staticmethod
    def validate_create(model_class, data):
        """
        Validate data for create operation.
        Returns a list of validation errors or empty list if valid.
        """
        return []  # Override in subclasses

    @staticmethod
    def validate_update(item, data):
        """
        Validate data for update operation.
        Returns a list of validation errors or empty list if valid.
        """
        return []  # Override in subclasses