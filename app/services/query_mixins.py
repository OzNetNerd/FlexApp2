"""Query builder mixins for common filtering operations."""

from typing import Any, Dict, List, Optional, Type, Union
from sqlalchemy.orm import Query
from app.utils.app_logging import get_logger

logger = get_logger()


class QueryBuilderMixin:
    """Mixin class providing common query builder methods."""

    def __init__(self, model_class=None):
        """
        Initialize with optional model class to allow standalone usage.

        Args:
            model_class: The SQLAlchemy model class this mixin operates on
        """
        self.model_class = model_class
        self.logger = logger

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

        logger.info(f"Applying text search filter: '{search_term}' across {len(fields)} fields")

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
            logger.info(f"Applying start date filter: >= {start_date}")
            query = query.filter(field >= start_date)

        if end_date:
            logger.info(f"Applying end date filter: <= {end_date}")
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
            logger.info(f"Applying minimum value filter: >= {min_value}")
            query = query.filter(field >= min_value)

        if max_value is not None:
            logger.info(f"Applying maximum value filter: <= {max_value}")
            query = query.filter(field <= max_value)

        return query

    def apply_sort(self, query: Query, model_class: Optional[Type[Any]] = None,
                  sort_by: Optional[str] = None, sort_order: str = 'asc') -> Query:
        """
        Apply sorting to a query.

        Args:
            query: The base SQLAlchemy query
            model_class: The SQLAlchemy model class (optional if set during init)
            sort_by: Field name to sort by
            sort_order: Sort direction ('asc' or 'desc')

        Returns:
            Modified query with sorting applied
        """
        if not sort_by:
            return query

        model_class = model_class or self.model_class
        if not model_class:
            logger.warning("No model class provided for sorting")
            return query

        logger.info(f"Applying sort by {sort_by} in {sort_order} order")

        try:
            # Get the model attribute to sort by
            sort_field = getattr(model_class, sort_by)

            # Apply descending order if requested
            if sort_order.lower() == 'desc':
                sort_field = sort_field.desc()

            return query.order_by(sort_field)

        except AttributeError:
            logger.warning(f"Sort field '{sort_by}' not found on model {model_class.__name__}")
            return query

    def apply_filters(self, query: Query, filters: Optional[Dict[str, Any]] = None,
                     model_class: Optional[Type[Any]] = None) -> Query:
        """
        Apply multiple filters to a query based on a filters dictionary.

        Args:
            query: The base SQLAlchemy query
            filters: Dictionary of filter conditions
            model_class: The SQLAlchemy model class (optional if set during init)

        Returns:
            Modified query with all filters applied
        """
        if not filters:
            return query

        model_class = model_class or self.model_class
        if not model_class:
            logger.warning("No model class provided for filtering")
            return query

        logger.info(f"Applying multiple filters: {filters}")

        # Apply standard equality filters
        for key, value in filters.items():
            # Skip special filter keys
            if key in ('sort_by', 'sort_order', 'search', 'min_value', 'max_value',
                       'start_date', 'end_date'):
                continue

            try:
                field = getattr(model_class, key)
                logger.info(f"Applying equality filter: {key} = {value}")
                query = query.filter(field == value)
            except AttributeError:
                logger.warning(f"Filter field '{key}' not found on model {model_class.__name__}")

        # Apply text search if specified
        if 'search' in filters and hasattr(model_class, 'searchable_fields'):
            fields = [getattr(model_class, field) for field in model_class.searchable_fields
                      if hasattr(model_class, field)]
            query = self.apply_text_search(query, filters['search'], *fields)

        # Apply sorting if specified
        if 'sort_by' in filters:
            query = self.apply_sort(
                query,
                model_class,
                filters.get('sort_by'),
                filters.get('sort_order', 'asc')
            )

        return query