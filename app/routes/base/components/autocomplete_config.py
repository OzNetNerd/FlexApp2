# app/routes/base/components/autocomplete_config.py
from typing import List
from dataclasses import dataclass


@dataclass
class AutoCompleteField:
    title: str
    id: str
    placeholder: str
    name: str
    data_url: str
    initial_ids: List[str]

def get_autocomplete_fields(relationships):
    """
    Generate the autocomplete fields configuration based on the given relationships.

    Args:
        relationships (list): A list of relationship data, each containing 'entity_type' and 'entity_id'.

    Returns:
        list: A list of autocomplete field configurations.
    """
    # Extract related user and company IDs from relationships
    related_user_ids = []
    related_company_ids = []

    for rel in relationships:
        if rel['entity_type'] == 'user':
            related_user_ids.append(rel['entity_id'])
        elif rel['entity_type'] == 'company':
            related_company_ids.append(rel['entity_id'])

    # Return the autocomplete fields configuration
    return [
        AutoCompleteField(
            title="Users",
            id="users-input",
            placeholder="Search for users...",
            name="users",
            data_url="/users/data",
            initial_ids=related_user_ids
        ),
        AutoCompleteField(
            title="Companies",
            id="companies-input",
            placeholder="Search for companies...",
            name="companies",
            data_url="/companies/data",
            initial_ids=related_company_ids
        )
    ]
