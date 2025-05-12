"""Base service module providing common CRUD operations."""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from app.utils.app_logging import get_logger
from app.models.base import db

logger = get_logger()

# Generic type for model
T = TypeVar('T')


class BaseService:
    """Base service class providing common CRUD operations for models."""

    def __init__(self, model_class: Type[T]):
        """
        Initialize base service with model class.

        Args:
            model_class: The SQLAlchemy model class this service operates on
        """
        self.model_class = model_class
        self.logger = logger

    def get_by_id(self, item_id: int) -> Optional[T]:
        """
        Get an item by ID.

        Args:
            item_id: The ID of the item to retrieve

        Returns:
            The item if found, None otherwise
        """
        self.logger.info(f"{self.__class__.__name__}: Retrieving item with ID {item_id}")
        item = self.model_class.query.get(item_id)

        if item:
            self.logger.info(f"{self.__class__.__name__}: Successfully retrieved item {item_id}")
        else:
            self.logger.info(f"{self.__class__.__name__}: Item with ID {item_id} not found")

        return item

    def get_all(self) -> List[T]:
        """
        Get all items.

        Returns:
            List of all items
        """
        self.logger.info(f"{self.__class__.__name__}: Retrieving all items")
        items = self.model_class.query.all()
        self.logger.info(f"{self.__class__.__name__}: Retrieved {len(items)} items")
        return items

    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new item.

        Args:
            data: Dictionary of attributes to set on the new item

        Returns:
            The newly created item
        """
        self.logger.info(f"{self.__class__.__name__}: Creating new item with data: {data}")
        item = self.model_class()

        for key, value in data.items():
            setattr(item, key, value)

        item.save()
        self.logger.info(f"{self.__class__.__name__}: Created new item with ID {item.id}")
        return item

    def update(self, item_id_or_obj: Union[int, T], update_data: Dict[str, Any]) -> T:
        """
        Update an item.

        Args:
            item_id_or_obj: Either an item ID or the item object to update
            update_data: Dictionary of attributes to update

        Returns:
            The updated item

        Raises:
            ValueError: If item_id_or_obj is an ID and no item with that ID exists
        """
        if isinstance(item_id_or_obj, int):
            item = self.get_by_id(item_id_or_obj)
            if not item:
                self.logger.error(f"{self.__class__.__name__}: Item with ID {item_id_or_obj} not found during update")
                raise ValueError(f"Item with ID {item_id_or_obj} not found")
        else:
            item = item_id_or_obj

        self.logger.info(f"{self.__class__.__name__}: Updating item {getattr(item, 'id', None)}")

        for key, value in update_data.items():
            setattr(item, key, value)

        item.save()
        self.logger.info(f"{self.__class__.__name__}: Successfully updated item {getattr(item, 'id', None)}")
        return item

    def delete(self, item_id: int) -> bool:
        """
        Delete an item by ID.

        Args:
            item_id: The ID of the item to delete

        Returns:
            True if successful, False if item not found

        Raises:
            Exception: If there's an error during deletion
        """
        self.logger.info(f"{self.__class__.__name__}: Deleting item with ID {item_id}")
        item = self.get_by_id(item_id)

        if not item:
            self.logger.error(f"{self.__class__.__name__}: Item with ID {item_id} not found during deletion")
            return False

        try:
            db.session.delete(item)
            db.session.commit()
            self.logger.info(f"{self.__class__.__name__}: Successfully deleted item {item_id}")
            return True
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"{self.__class__.__name__}: Error deleting item {item_id}: {str(e)}")
            raise

    def count(self) -> int:
        """
        Count the total number of items.

        Returns:
            Total count of items
        """
        self.logger.info(f"{self.__class__.__name__}: Counting total items")
        count = self.model_class.query.count()
        self.logger.info(f"{self.__class__.__name__}: Total items: {count}")
        return count