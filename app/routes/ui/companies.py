from app.routes.base.components.form_handler import Tab, TabSection, TabEntry
from typing import List


def get_company_tabs(item: dict, include_metadata: bool = False) -> List[Tab]:
    """Returns the list of tabs with data injected from the item dictionary.

    Args:
        item (dict): Dictionary of field values to populate into TabEntry.value.
        include_metadata (bool): Whether to include the Metadata tab.

    Returns:
        List[Tab]: List of populated Tab objects.
    """
    # Company Details section
    company_details_section = TabSection(section_name="Company Details", entries=[
        TabEntry(entry_name="name", label="Name", type="text", required=True, readonly=False, value=item.get("name")),
        TabEntry(entry_name="description", label="Description", type="text", readonly=False, value=item.get("description")),
    ])

    # CRISP Score section
    crisp_score_section = TabSection(section_name="CRISP Score", entries=[
        TabEntry(entry_name="crisp", label="CRISP", type="custom", readonly=False, value=item.get("crisp")),
    ])

    # About tab
    about_tab = Tab(tab_name="About", sections=[company_details_section])

    # Insights tab
    insights_tab = Tab(tab_name="Insights", sections=[crisp_score_section])

    tabs = [about_tab, insights_tab]

    # Optionally add metadata
    if include_metadata:
        metadata_section = TabSection(section_name="Metadata", entries=[
            TabEntry(entry_name="created_at", label="Created At", type="readonly", readonly=True, value=item.get("created_at")),
            TabEntry(entry_name="updated_at", label="Updated At", type="readonly", readonly=True, value=item.get("updated_at")),
        ])
        metadata_tab = Tab(tab_name="Metadata", sections=[metadata_section])
        tabs.append(metadata_tab)

    return tabs
