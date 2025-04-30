from typing import Any, Dict, List, Optional

from app.routes.base_context import AppContext
from app.utils.app_logging import get_logger

logger = get_logger()


class ApiContext(AppContext):
    """Base context class for API responses."""

    def __init__(self, **kwargs):
        """Initialize the API context."""
        super().__init__(**kwargs)


class ListApiContext(ApiContext):
    """Context class for list API responses."""

    def __init__(
        self,
        entity_table_name: str,
        items: List[Any],
        total_count: Optional[int] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs,
    ):
        """Initialize a list API context."""
        super().__init__(entity_table_name=entity_table_name, **kwargs)

        self.items = items
        self.total_count = total_count or len(items)

        # Pagination info
        if page is not None:
            self.page = page
            self.per_page = per_page or len(items)

    def to_dict(self):
        """Format response with items and metadata."""
        base_dict = super().to_dict()

        # Convert items to dictionaries
        items_data = []
        for item in self.items:
            if hasattr(item, "to_dict"):
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
            },
        }

        # Add pagination if present
        if hasattr(self, "page"):
            result["meta"]["pagination"] = {
                "page": self.page,
                "per_page": self.per_page,
                "total_pages": (self.total_count + self.per_page - 1) // self.per_page,
            }

        # Add other attributes
        for key, value in base_dict.items():
            if key not in ["entity_table_name", "items", "total_count", "page", "per_page"]:
                result[key] = value

        return result


class EntityApiContext(ApiContext):
    """Context class for single entity API responses."""

    def __init__(self, entity_table_name: str, entity: Any = None, entity_id: Any = None, **kwargs):
        """Initialize an entity API context."""
        super().__init__(entity_table_name=entity_table_name, **kwargs)

        self.entity = entity
        self.entity_id = entity_id or getattr(entity, "id", None)

    def to_dict(self):
        """Format response with entity data."""
        base_dict = super().to_dict()

        # Create response structure
        result = {"meta": {"entity_type": self.entity_table_name}}

        # Add entity data
        if self.entity:
            if hasattr(self.entity, "to_dict"):
                result["data"] = self.entity.to_dict()
            elif isinstance(self.entity, dict):
                result["data"] = self.entity
            else:
                result["data"] = {"id": self.entity_id, "value": str(self.entity)}
        else:
            result["data"] = {"id": self.entity_id}

        # Add other attributes
        for key, value in base_dict.items():
            if key not in ["entity_table_name", "entity", "entity_id"]:
                result[key] = value

        return result


class ErrorApiContext(ApiContext):
    """Context class for error API responses."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
        field_errors: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """Initialize an error API context."""
        super().__init__(**kwargs)

        self.message = message
        self.status_code = status_code

        if error_code:
            self.error_code = error_code

        if field_errors:
            self.field_errors = field_errors

    def to_dict(self):
        """Format error response."""
        base_dict = super().to_dict()

        result = {"error": {"message": self.message, "status_code": self.status_code}}

        # Add error code if present
        if hasattr(self, "error_code"):
            result["error"]["code"] = self.error_code

        # Add field errors if present
        if hasattr(self, "field_errors"):
            result["error"]["fields"] = self.field_errors

        # Add other attributes
        for key, value in base_dict.items():
            if key not in ["message", "status_code", "error_code", "field_errors"]:
                result[key] = value

        return result
