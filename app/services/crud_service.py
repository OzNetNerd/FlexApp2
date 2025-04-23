# app/services/crud_service.py

import traceback
from datetime import datetime
from typing import Any, Type

from app.models.base import db
from app.models.mixins import ValidatorMixin
from app.utils.app_logging import get_logger

logger = get_logger()


class CRUDService:
    """
    Generic CRUD service for SQLAlchemy models.

    This class abstracts away common patterns for creating, reading,
    updating, and deleting models. Intended to be subclassed or instantiated
    per-model for reuse and testability.
    """

    def __init__(self, model_class: Type, required_fields: list[str] = None):
        """
        Initialize the CRUDService.

        Args:
            model_class (Type): The SQLAlchemy model class to operate on.
            required_fields (list[str], optional): Fields that must be present on create.
        """
        self.model_class = model_class
        self.required_fields = required_fields or []

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
                        ftype = filter_config.get("type")
                        fval = filter_config.get("filter")
                        logger.debug(f"Applying filter on {col_id}: {ftype}={fval}")
                        if ftype == "contains":
                            query = query.filter(column.ilike(f"%{fval}%"))
                        elif ftype == "equals":
                            query = query.filter(column == fval)

            if hasattr(self.model_class, sort_column):
                column = getattr(self.model_class, sort_column)
                query = query.order_by(column.desc() if sort_direction == "desc" else column)

            return query.paginate(page=page, per_page=per_page, error_out=False)

        except Exception as e:
            logger.error(f"❌ Error in get_all for {self.model_class.__name__}: {e}")
            logger.error(traceback.format_exc())
            raise

    def get_by_id(self, entity_id: int) -> Any:
        """Fetch a single instance by its primary key."""
        try:
            return db.session.get(self.model_class, entity_id)
        except Exception as e:
            logger.error(f"❌ Error fetching {self.model_class.__name__} id={entity_id}: {e}")
            raise

    def create(self, data: dict) -> Any:
        """
        Create a new instance after validating required fields and handling extra attrs.

        Raises:
            ValueError: If any required fields are missing.
        """
        try:
            # 1) enforce required fields
            missing = [f for f in self.required_fields if not data.get(f)]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")

            # 2) pull off any non-column properties to set after flush
            property_attrs = {}
            for key in list(data):
                if key not in self.model_class.__table__.columns:
                    property_attrs[key] = data.pop(key)

            # 3) instantiate and persist
            entity = self.model_class(**data)
            db.session.add(entity)
            db.session.flush()  # get PK without committing

            # 4) assign back any extra attributes
            for key, value in property_attrs.items():
                try:
                    setattr(entity, key, value)
                except Exception as e:
                    logger.warning(f"Could not set property {key}: {e}")

            db.session.commit()
            return entity

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Error creating {self.model_class.__name__}: {e}")
            logger.error(traceback.format_exc())
            raise

    def update(self, entity: Any, data: dict) -> Any:
        """
        Update an existing instance.

        Args:
            entity (Any): The existing instance.
            data (dict): New values.

        Returns:
            Any: The updated instance.
        """
        try:
            # strip out empty strings and convert dates if needed
            data = {k: v for k, v in data.items() if v != ""}
            data = self._convert_dates(data)

            # model-level validation
            if isinstance(entity, ValidatorMixin):
                errors = entity.validate_update(data)
                if errors:
                    raise ValueError(f"Validation failed: {errors}")

            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            db.session.commit()
            return entity

        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Error updating {entity.__class__.__name__} id={getattr(entity, 'id', 'unknown')}: {e}")
            logger.error(traceback.format_exc())
            raise

    def delete(self, entity_or_id: Any) -> bool:
        """
        Delete an instance by ID or instance.

        Returns:
            bool: True if deletion succeeded.
        """
        if isinstance(entity_or_id, int):
            entity = self.get_by_id(entity_or_id)
        else:
            entity = entity_or_id

        try:
            db.session.delete(entity)
            db.session.commit()
            logger.info(f"✅ Deleted {entity.__class__.__name__} id={entity.id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Error deleting {entity.__class__.__name__} id={getattr(entity, 'id', 'unknown')}: {e}")
            raise
