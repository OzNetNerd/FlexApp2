# app/routes/base/components/autocomplete.py
from typing import List
from dataclasses import dataclass

import logging

logger = logging.getLogger(__name__)


@dataclass
class AutoCompleteField:
    title: str
    id: str
    placeholder: str
    name: str
    data_url: str
    related_ids: List[str]


# def get_autocomplete_fields(relationships):
#     """
#     Generate the autocomplete fields configuration based on the given relationships.
#
#     Args:
#         relationships (list): A list of relationship data, each containing 'entity_type' and 'entity_id'.
#
#     Returns:
#         list: A list of autocomplete field configurations.
#     """
#     # Extract related user and company IDs from relationships
#     related_user_ids = []
#     related_company_ids = []
#
#     for rel in relationships:
#         if rel['entity_type'] == 'user':
#             related_user_ids.append(rel['entity_id'])
#         elif rel['entity_type'] == 'company':
#             related_company_ids.append(rel['entity_id'])
#
#     # Return the autocomplete fields configuration
#     return [
#         AutoCompleteField(
#             title="Users",
#             id="users-input",
#             placeholder="Search for users...",
#             name="users",
#             data_url="/users/data",
#             related_ids=related_user_ids
#         ),
#         AutoCompleteField(
#             title="Companies",
#             id="companies-input",
#             placeholder="Search for companies...",
#             name="companies",
#             data_url="/companies/data",
#             related_ids=related_company_ids
#         )
#     ]


def get_autocomplete_field(title, relationships=None, field_id=None, placeholder=None, name=None, data_url=None):
    """Get an AutoCompleteField instance with defaults derived from the title."""
    title_lower = title.lower()
    field_id = field_id or f"{title_lower}-input"
    placeholder = placeholder or f"Search for {title_lower}..."
    name = name or title_lower
    data_url = data_url or f"/{title_lower}/data"

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
    field = AutoCompleteField(title=title, id=field_id, placeholder=placeholder, name=name, data_url=data_url, related_ids=related_ids)
    return field
