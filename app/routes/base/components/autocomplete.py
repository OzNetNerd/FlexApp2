# app/routes/base/components/autocomplete.py
from typing import List
from dataclasses import dataclass

import logging
from app.services.relationship_service import RelationshipService

logger = logging.getLogger(__name__)


@dataclass
class AutoCompleteField:
    title: str
    id: str
    placeholder: str
    name: str
    data_url: str
    initial_ids: List[str]

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
#             initial_ids=related_user_ids
#         ),
#         AutoCompleteField(
#             title="Companies",
#             id="companies-input",
#             placeholder="Search for companies...",
#             name="companies",
#             data_url="/companies/data",
#             initial_ids=related_company_ids
#         )
#     ]



def create_autocomplete_field(title, initial_ids=None, field_id=None, placeholder=None, name=None, data_url=None):
    """
    Create an AutoCompleteField instance using defaults derived from the title if parameters
    are not specified.
    """
    title_lower = title.lower()
    field_id = field_id or f"{title_lower}-input"
    placeholder = placeholder or f"Search for {title_lower}..."
    name = name or title_lower
    # Assumes a plural URL pattern; adjust if necessary.
    data_url = data_url or f"/{title_lower}s/data"
    return AutoCompleteField(
        title=title,
        id=field_id,
        placeholder=placeholder,
        name=name,
        data_url=data_url,
        initial_ids=initial_ids or []
    )


def get_autocomplete_fields(relationships, model_name=""):
    """
    Build a list of autocomplete fields based on relationships.
    For User models, extract related user and company IDs.
    """
    if model_name == "User":
        related_user_ids = [rel['entity_id'] for rel in relationships if rel['entity_type'] == 'user']
        related_company_ids = [rel['entity_id'] for rel in relationships if rel['entity_type'] == 'company']

        return [
            create_autocomplete_field(
                title="Users",
                initial_ids=related_user_ids
            ),
            create_autocomplete_field(
                title="Companies",
                initial_ids=related_company_ids
            )
        ]
    # Add additional model-specific logic here if needed.
    return []