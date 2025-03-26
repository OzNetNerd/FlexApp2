from typing import Type
from app.models.base import db
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)


class CRUDService:
    """
    Service layer for CRUD operations on database models.
    Separates business logic from presentation concerns.
    """

    def __init__(self, model_class: Type):
        self.model_class = model_class

    def get_all(
        self, page=1, per_page=15, sort_column="id", sort_direction="asc", filters=None
    ):
        try:
            query = self.model_class.query

            if filters:
                for col_id, filter_config in filters.items():
                    if hasattr(self.model_class, col_id):
                        column = getattr(self.model_class, col_id)
                        filter_type = filter_config.get("type")
                        filter_value = filter_config.get("filter")
                        logger.debug(
                            f"Applying filter on {col_id}: {filter_type}={filter_value}"
                        )
                        if filter_type == "contains":
                            query = query.filter(column.ilike(f"%{filter_value}%"))
                        elif filter_type == "equals":
                            query = query.filter(column == filter_value)

            if hasattr(self.model_class, sort_column):
                column = getattr(self.model_class, sort_column)
                query = query.order_by(
                    column.desc() if sort_direction == "desc" else column
                )

            items = query.paginate(page=page, per_page=per_page, error_out=False)
            return items

        except Exception as e:
            logger.error(f"Error in get_all for {self.model_class.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def get_by_id(self, item_id):
        try:
            return self.model_class.query.get_or_404(item_id)
        except Exception as e:
            logger.error(
                f"Error in get_by_id for {self.model_class.__name__} with id {item_id}: {str(e)}"
            )
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _convert_dates(self, data: dict) -> dict:
        """
        Converts string-formatted dates (e.g. '2025-03-27') into Python datetime objects.

        Args:
            data (dict): Form data

        Returns:
            dict: Transformed data
        """
        if "due_date" in data and isinstance(data["due_date"], str):
            try:
                data["due_date"] = datetime.strptime(data["due_date"], "%Y-%m-%d")
            except ValueError:
                logger.warning("Invalid due_date format; setting to None")
                data["due_date"] = None
        return data

    def create(self, data):
        try:
            data = {k: v for k, v in data.items() if v != ""}
            data = self._convert_dates(data)  # ✅ Fix for Task due_date
            item = self.model_class(**data)
            db.session.add(item)
            db.session.commit()
            return item
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def update(self, item, data):
        try:
            data = {k: v for k, v in data.items() if v != ""}
            data = self._convert_dates(data)  # ✅ Fix for Task due_date
            for key, value in data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            db.session.commit()
            return item
        except Exception as e:
            db.session.rollback()
            logger.error(
                f"Error updating {item.__class__.__name__} with id {item.id}: {str(e)}"
            )
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def delete(self, item):
        try:
            db.session.delete(item)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(
                f"Error deleting {item.__class__.__name__} with id {item.id}: {str(e)}"
            )
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def validate_create(self, data):
        return []

    def validate_update(self, item, data):
        return []
