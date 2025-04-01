from app.routes.base.components.entity_handler import Tab, TabSection, TabEntry
from typing import List


def get_company_tabs(item: dict) -> List[Tab]:
    """Returns the list of tabs with data injected from the item dictionary.

    Args:
        item (dict): Dictionary of field values to populate into TabEntry.value.

    Returns:
        List[Tab]: List of populated Tab objects.
    """
    # Company Details section
    company_details_section = TabSection(section_name="Company Details", entries=[
        TabEntry(entry_name="name", label="Name", type="text", required=True, value=item.get("name")),
        TabEntry(entry_name="description", label="Description", type="text", value=item.get("description")),
    ])

    # CRISP Score section
    crisp_score_section = TabSection(section_name="CRISP Score", entries=[
        TabEntry(entry_name="crisp", label="CRISP", type="custom", value=item.get("crisp")),
    ])

    # About tab
    about_tab = Tab(tab_name="About", sections=[company_details_section])

    # Insights tab
    insights_tab = Tab(tab_name="Insights", sections=[crisp_score_section])

    # Metadata tab
    metadata_section = TabSection(section_name="Metadata", entries=[
        TabEntry(entry_name="created_at", label="Created At", type="readonly", value=item.get("created_at")),
        TabEntry(entry_name="updated_at", label="Updated At", type="readonly", value=item.get("updated_at")),
    ])
    metadata_tab = Tab(tab_name="Metadata", sections=[metadata_section])

    # Relationships section for users and companies
    relationships_section = TabSection(
        section_name="Mappings",
        entries=[
            TabEntry(entry_name="users", label="Users", type="custom", value=item.get("users")),
            TabEntry(entry_name="companies", label="Companies", type="custom", value=item.get("companies")),
        ]
    )

    relationships_tab = Tab(
        tab_name="Relationships",
        sections=[relationships_section]
    )

    tabs = [about_tab, insights_tab, metadata_tab, relationships_tab]


    return tabs
