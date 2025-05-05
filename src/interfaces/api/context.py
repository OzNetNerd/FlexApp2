"""Context classes for API responses.

This module provides standardized context classes for API responses,
ensuring consistent formatting and structure across all API endpoints.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class EntityApiContext:
    """Context for a single entity API response.

    Attributes:
        entity_table_name: Name of the entity's table.
        entity: The entity object.
        message: Optional message to include in the response.
    """
    entity_table_name: str
    entity: Any
    message: Optional[str] = None


@dataclass
class ListApiContext:
    """Context for a list of entities API response.

    Attributes:
        entity_table_name: Name of the entity's table.
        items: List of entity objects.
        total_count: Optional total count of items.
    """
    entity_table_name: str
    items: List[Any]
    total_count: Optional[int] = None


@dataclass
class ErrorApiContext:
    """Context for an error API response.

    Attributes:
        message: Error message.
        status_code: HTTP status code.
        details: Optional additional error details.
    """
    message: str
    status_code: int = 400
    details: Optional[Dict[str, Any]] = None