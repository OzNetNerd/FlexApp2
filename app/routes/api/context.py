# api/context.py

import logging
from typing import Any, Optional, Dict, List

logger = logging.getLogger(__name__)


class APIContext:
    """Base context class for API responses."""

    def __init__(self, **kwargs):
        """Initialize the API context with provided attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)
            logger.debug(f"Set attribute '{key}' = {value}")

    def __repr__(self):
        """Return a detailed string representation of the context."""
        attributes = ", ".join(f"{key}={repr(value)}" for key, value in vars(self).items() if not key.startswith("_"))
        return f"{self.__class__.__name__}({attributes})"

    def to_dict(self):
        """Convert context to dictionary for response serialization."""
        return {key: value for key, value in vars(self).items() if not key.startswith("_")}


class ListAPIContext(APIContext):
    """Context class for list API responses."""

    def __init__(self, entity_table_name: str, items: List[Any],
                 total_count: Optional[int] = None, page: Optional[int] = None,
                 per_page: Optional[int] = None, **kwargs):
        """Initialize a list API context."""
        self.entity_table_name = entity_table_name
        self.items = items
        self.total_count = total_count or len(items)

        # Pagination info (if applicable)
        if page is not None:
            self.page = page
            self.per_page = per_page or len(items)

        super().__init__(**kwargs)

    def to_dict(self):
        """Convert to response dictionary with pagination if applicable."""
        base_dict = super().to_dict()

        # Convert items to dictionaries if they have to_dict method
        items_data = []
        for item in self.items:
            if hasattr(item, 'to_dict'):
                items_data.append(item.to_dict())
            elif isinstance(item, dict):
                items_data.append(item)
            else:
                items_data.append(str(item))

        result = {
            "data": items_data,
            "meta": {
                "total": self.total_count,
                "entity_type": self.entity_table_name,
            }
        }

        # Add pagination metadata if present
        if hasattr(self, 'page'):
            result["meta"]["pagination"] = {
                "page": self.page,
                "per_page": self.per_page,
                "total_pages": (self.total_count + self.per_page - 1) // self.per_page
            }

        # Add any additional attributes
        for key, value in base_dict.items():
            if key not in ["entity_table_name", "items", "total_count", "page", "per_page"]:
                result[key] = value

        return result


class EntityAPIContext(APIContext):
    """Context class for single entity API responses."""

    def __init__(self, entity_table_name: str, entity: Any = None, entity_id: Any = None, **kwargs):
        """Initialize an entity API context."""
        self.entity_table_name = entity_table_name
        self.entity = entity
        self.entity_id = entity_id or getattr(entity, 'id', None)

        super().__init__(**kwargs)

    def to_dict(self):
        """Convert to response dictionary with entity data."""
        base_dict = super().to_dict()

        # Create the response structure
        result = {"meta": {"entity_type": self.entity_table_name}}

        # Add entity data
        if self.entity:
            if hasattr(self.entity, 'to_dict'):
                result["data"] = self.entity.to_dict()
            elif isinstance(self.entity, dict):
                result["data"] = self.entity
            else:
                result["data"] = {"id": self.entity_id, "value": str(self.entity)}
        else:
            result["data"] = {"id": self.entity_id}

        # Add any additional attributes
        for key, value in base_dict.items():
            if key not in ["entity_table_name", "entity", "entity_id"]:
                result[key] = value

        return result


class ErrorAPIContext(APIContext):
    """Context class for error API responses."""

    def __init__(self, message: str, status_code: int = 400, error_code: Optional[str] = None,
                 field_errors: Optional[Dict[str, str]] = None, **kwargs):
        """Initialize an error API context."""
        self.message = message
        self.status_code = status_code

        if error_code:
            self.error_code = error_code

        if field_errors:
            self.field_errors = field_errors

        super().__init__(**kwargs)

    def to_dict(self):
        """Convert to error response dictionary."""
        base_dict = super().to_dict()

        result = {
            "error": {
                "message": self.message,
                "status_code": self.status_code
            }
        }

        # Add error code if present
        if hasattr(self, 'error_code'):
            result["error"]["code"] = self.error_code

        # Add field errors if present
        if hasattr(self, 'field_errors'):
            result["error"]["fields"] = self.field_errors

        # Add any additional attributes
        for key, value in base_dict.items():
            if key not in ["message", "status_code", "error_code", "field_errors"]:
                result[key] = value

        return result