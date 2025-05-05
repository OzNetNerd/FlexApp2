"""Autocomplete field value object for UI forms.

This module provides a value object representing an autocomplete field and
utilities for creating fields with appropriate defaults.
"""

from dataclasses import dataclass
from typing import List, Optional

from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class AutoCompleteField:
    """Value object representing an autocomplete input field.

    Attributes:
        title: Display title for the field.
        id: HTML ID attribute.
        placeholder: Placeholder text.
        name: Form field name.
        data_api_url: URL for data source.
        related_ids: List of related entity IDs.
    """
    title: str
    id: str
    placeholder: str
    name: str
    data_api_url: str
    related_ids: List[str]


def create_autocomplete_field(
        title: str,
        relationships: Optional[List[dict]] = None,
        field_id: Optional[str] = None,
        placeholder: Optional[str] = None,
        name: Optional[str] = None,
        data_api_url: Optional[str] = None
) -> AutoCompleteField:
    """Create an AutoCompleteField with sensible defaults.

    Args:
        title: Display title for the field.
        relationships: Optional list of entity relationships.
        field_id: Optional HTML ID attribute (defaults to title-based ID).
        placeholder: Optional placeholder text (defaults to title-based text).
        name: Optional form field name (defaults to lowercase title).
        data_api_url: Optional data API URL (defaults to title-based URL).

    Returns:
        Configured AutoCompleteField instance.
    """
    title_lower = title.lower()
    field_id = field_id or f"{title_lower}-input"
    placeholder = placeholder or f"Search for {title_lower}..."
    name = name or title_lower
    data_api_url = data_api_url or f"/api/{title_lower}"

    if title_lower == "companies":
        entity_type = "company"
    else:
        entity_type = title_lower.rstrip("s")

    logger.info(f"Derived entity_type {entity_type!r} from title {title!r}")

    related_ids = []
    if relationships is not None:
        related_ids = [rel["entity_id"] for rel in relationships if rel.get("entity_type") == entity_type]
        logger.info(f"Extracted related IDs for entity_type {entity_type!r}: {related_ids!r}")

    return AutoCompleteField(
        title=title,
        id=field_id,
        placeholder=placeholder,
        name=name,
        data_api_url=data_api_url,
        related_ids=related_ids,
    )