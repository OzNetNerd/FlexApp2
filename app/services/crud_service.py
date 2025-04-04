import logging
import traceback
from typing import Type, Any
from datetime import datetime
from app.models.base import db
from app.models.mixins import ValidatorMixin

logger = logging.getLogger(__name__)


class CRUDService:
    """
    Generic CRUD service for SQLAlchemy models.

    This class abstracts away common patterns for creating, reading,
    updating, and deleting models. Intended to be subclassed or instantiated
    per-model for reuse and testability.
    """

    def __init__(self, model_class: Type):
        """
        Initialize the CRUDService.

        Args:
            model_class (Type): The SQLAlchemy model class to operate on.
        """
        self.model_class = model_class

    def get_all(
        self,
        page: int = 1,
        per_page: int = 15,
        sort_column: str = "id",
        sort_direction: str = "asc",
        filters: dict | None = None,
    ) -> Any:
        """
        Retrieve paginated and optionally filtered results.

        Args:
            page (int): Page number.
            per_page (int): Results per page.
            sort_column (str): Field to sort by.
            sort_direction (str): 'asc' or 'desc'.
            filters (dict | None): Column filters.

        Returns:
            Pagination: A pagination object with results.
        """
        try:
            query = self.model_class.query

            if filters:
                for col_id, filter_config in filters.items():
                    if hasattr(self.model_class, col_id):
                        column = getattr(self.model_class, col_id)
                        filter_type = filter_config.get("type")
                        filter_value = filter_config.get("filter")
                        logger.debug(f"Applying filter on {col_id}: {filter_type}={filter_value}")
                        if filter_type == "contains":
                            query = query.filter(column.ilike(f"%{filter_value}%"))
                        elif filter_type == "equals":
                            query = query.filter(column == filter_value)

            if hasattr(self.model_class, sort_column):
                column = getattr(self.model_class, sort_column)
                query = query.order_by(column.desc() if sort_direction == "desc" else column)

            return query.paginate(page=page, per_page=per_page, error_out=False)

        except Exception as e:
            logger.error(f"❌  Error in get_all for {self.model_class.__name__}: {e}")
            logger.error(traceback.format_exc())
            raise

    def get_by_id(self, item_id: int) -> Any:
        """
        Fetch a single record by its ID.

        Args:
            item_id (int): Primary key.

        Returns:
            Any: The found model instance or 404 error.
        """
        try:
            return self.model_class.query.get_or_404(item_id)
        except Exception as e:
            logger.error(f"❌  Error in get_by_id for {self.model_class.__name__} with id {item_id}: {e}")
            logger.error(traceback.format_exc())
            raise

    def _convert_dates(self, data: dict) -> dict:
        """
        Converts any date strings into datetime objects (currently only handles 'due_date').

        Args:
            data (dict): Input form data.

        Returns:
            dict: Transformed data.
        """
        if "due_date" in data and isinstance(data["due_date"], str):
            try:
                data["due_date"] = datetime.strptime(data["due_date"], "%Y-%m-%d")
            except ValueError:
                logger.warning("Invalid due_date format; setting to None")
                data["due_date"] = None
        return data

    def create(self, data: dict) -> Any:
        """
        Create and persist a new instance.

        Args:
            data (dict): Form data.

        Returns:
            Any: The created instance.
        """
        try:
            data = {k: v for k, v in data.items() if v != ""}
            data = self._convert_dates(data)

            if issubclass(self.model_class, ValidatorMixin):
                errors = self.model_class().validate_create(data)
                if errors:
                    raise ValueError(f"Validation failed: {errors}")

            item = self.model_class(**data)
            db.session.add(item)
            db.session.commit()
            return item
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌  Error creating {self.model_class.__name__}: {e}")
            logger.error(traceback.format_exc())
            raise

    def update(self, item: Any, data: dict) -> Any:
        """
        Update an existing instance.

        Args:
            item (Any): The existing instance.
            data (dict): New values.

        Returns:
            Any: The updated instance.
        """
        try:
            data = {k: v for k, v in data.items() if v != ""}
            data = self._convert_dates(data)

            if isinstance(item, ValidatorMixin):
                errors = item.validate_update(data)
                if errors:
                    raise ValueError(f"Validation failed: {errors}")

            for key, value in data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            db.session.commit()
            return item
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌  Error updating {item.__class__.__name__} with id {item.id}: {e}")
            logger.error(traceback.format_exc())
            raise

    def delete(self, item: Any) -> bool:
        """
        Delete an instance from the database.

        Args:
            item (Any): Instance to be deleted.

        Returns:
            bool: True if successful.
        """
        try:
            db.session.delete(item)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌  Error deleting {item.__class__.__name__} with id {item.id}: {e}")
            logger.error(traceback.format_exc())
            raise

    def validate_create(self, data: dict) -> list:
        """
        Validate input data for creation. Override in subclasses.

        Args:
            data (dict): Input data.

        Returns:
            list: List of validation errors (empty if valid).
        """
        return []

    def validate_update(self, item: Any, data: dict) -> list:
        """
        Validate input data for updating. Override in subclasses.

        Args:
            item (Any): Existing instance.
            data (dict): Updated data.

        Returns:
            list: List of validation errors (empty if valid).
        """
        return []
