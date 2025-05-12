"""Base service classes for application."""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Query
from app.utils.app_logging import get_logger
from app.models.base import db

# Generic type for model
T = TypeVar('T')


class ServiceBase:
    """Foundation for all services with common functionality."""

    def __init__(self, model_class=None):
        """
        Initialize service with optional model class.

        Args:
            model_class: The SQLAlchemy model class this service operates on
        """
        self.model_class = model_class
        self.logger = get_logger()
        self.logger.info(f"{self.__class__.__name__}: Initializing service")


class CRUDService(ServiceBase):
    """Service class providing common CRUD operations for models."""

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


class QueryService(ServiceBase):
    """Service class providing query builder methods."""

    def apply_text_search(self, query: Query, search_term: str, *fields) -> Query:
        """
        Apply a text search filter across multiple fields.

        Args:
            query: The base SQLAlchemy query
            search_term: The search term to look for
            *fields: Model fields to search in

        Returns:
            Modified query with text search filters
        """
        if not search_term or not fields:
            return query

        self.logger.info(f"Applying text search filter: '{search_term}' across {len(fields)} fields")

        # Format for LIKE query
        formatted_term = f"%{search_term}%"

        # Build OR conditions for each field
        conditions = []
        for field in fields:
            conditions.append(field.ilike(formatted_term))

        # Apply OR conditions to query
        return query.filter(*(conditions))

    def apply_date_range(self, query: Query, field, start_date: Optional[Any] = None,
                         end_date: Optional[Any] = None) -> Query:
        """
        Apply a date range filter to a query.

        Args:
            query: The base SQLAlchemy query
            field: The date field to filter on
            start_date: The start date (inclusive)
            end_date: The end date (inclusive)

        Returns:
            Modified query with date range filters
        """
        if start_date:
            self.logger.info(f"Applying start date filter: >= {start_date}")
            query = query.filter(field >= start_date)

        if end_date:
            self.logger.info(f"Applying end date filter: <= {end_date}")
            query = query.filter(field <= end_date)

        return query

    def apply_numeric_range(self, query: Query, field, min_value: Optional[Union[int, float]] = None,
                            max_value: Optional[Union[int, float]] = None) -> Query:
        """
        Apply a numeric range filter to a query.

        Args:
            query: The base SQLAlchemy query
            field: The numeric field to filter on
            min_value: The minimum value (inclusive)
            max_value: The maximum value (inclusive)

        Returns:
            Modified query with numeric range filters
        """
        if min_value is not None:
            self.logger.info(f"Applying minimum value filter: >= {min_value}")
            query = query.filter(field >= min_value)

        if max_value is not None:
            self.logger.info(f"Applying maximum value filter: <= {max_value}")
            query = query.filter(field <= max_value)

        return query

    def apply_sort(self, query: Query, sort_by: Optional[str] = None,
                   sort_order: str = 'asc') -> Query:
        """
        Apply sorting to a query.

        Args:
            query: The base SQLAlchemy query
            sort_by: Field name to sort by
            sort_order: Sort direction ('asc' or 'desc')

        Returns:
            Modified query with sorting applied
        """
        if not sort_by or not self.model_class:
            return query

        self.logger.info(f"Applying sort by {sort_by} in {sort_order} order")

        try:
            # Get the model attribute to sort by
            sort_field = getattr(self.model_class, sort_by)

            # Apply descending order if requested
            if sort_order.lower() == 'desc':
                sort_field = sort_field.desc()

            return query.order_by(sort_field)

        except AttributeError:
            self.logger.warning(f"Sort field '{sort_by}' not found on model {self.model_class.__name__}")
            return query

    def apply_filters(self, query: Query, filters: Optional[Dict[str, Any]] = None) -> Query:
        """
        Apply multiple filters to a query based on a filters dictionary.

        Args:
            query: The base SQLAlchemy query
            filters: Dictionary of filter conditions

        Returns:
            Modified query with all filters applied
        """
        if not filters or not self.model_class:
            return query

        self.logger.info(f"Applying multiple filters: {filters}")

        # Apply standard equality filters
        for key, value in filters.items():
            # Skip special filter keys
            if key in ('sort_by', 'sort_order', 'search', 'min_value', 'max_value',
                       'start_date', 'end_date'):
                continue

            try:
                field = getattr(self.model_class, key)
                self.logger.info(f"Applying equality filter: {key} = {value}")
                query = query.filter(field == value)
            except AttributeError:
                self.logger.warning(f"Filter field '{key}' not found on model {self.model_class.__name__}")

        # Apply text search if specified
        if 'search' in filters and hasattr(self.model_class, 'searchable_fields'):
            fields = [getattr(self.model_class, field) for field in self.model_class.searchable_fields
                      if hasattr(self.model_class, field)]
            query = self.apply_text_search(query, filters['search'], *fields)

        # Apply sorting if specified
        if 'sort_by' in filters:
            query = self.apply_sort(
                query,
                filters.get('sort_by'),
                filters.get('sort_order', 'asc')
            )

        return query


class ServiceRegistry:
    """Registry of service instances for dependency injection."""

    _instances = {}

    @classmethod
    def get(cls, service_class):
        """
        Get or create service instance.

        Args:
            service_class: The service class to retrieve

        Returns:
            Instance of the service class
        """
        if service_class not in cls._instances:
            cls._instances[service_class] = service_class()
        return cls._instances[service_class]