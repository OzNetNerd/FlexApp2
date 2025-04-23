# app/routes/base/components/autocomplete.py
from typing import List
from dataclasses import dataclass

from app.utils.app_logging import get_logger
logger = get_logger()


@dataclass
class AutoCompleteField:
    title: str
    id: str
    placeholder: str
    name: str
    data_api_url: str
    related_ids: List[str]


def get_autocomplete_field(title, relationships=None, field_id=None, placeholder=None, name=None, data_api_url=None):
    """Get an AutoCompleteField instance with defaults derived from the title."""
    title_lower = title.lower()
    field_id = field_id or f"{title_lower}-input"
    placeholder = placeholder or f"Search for {title_lower}..."
    name = name or title_lower
    data_api_url = data_api_url or f"/api//{title_lower}"

    # Fix entity type derivation with special cases
    if title_lower == "companies":
        entity_type = "company"
    else:
        entity_type = title_lower.rstrip("s")

    logger.info(f"Derived entity_type '{entity_type}' from title '{title}'.")

    related_ids = []
    if relationships is not None:
        related_ids = [rel["entity_id"] for rel in relationships if rel.get("entity_type") == entity_type]
        logger.info(f"Extracted related IDs for entity_type '{entity_type}': {related_ids}")

    # Make sure to use related_ids to match template expectations
    field = AutoCompleteField(
        title=title, id=field_id, placeholder=placeholder, name=name, data_api_url=data_api_url, related_ids=related_ids
    )
    return field
