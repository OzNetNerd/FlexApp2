from app.routes.base.components.form_handler import Tab, TabSection, TabEntry
from typing import List


def get_users_tabs(item: dict) -> List[Tab]:
    """Returns the list of user-related tabs with data populated from the item dictionary.

    Args:
        item (dict): Dictionary of field values to populate into TabEntry.value.

    Returns:
        List[Tab]: List of populated Tab objects.
    """
    # Basic Info section
    basic_info_section = TabSection(section_name="Basic Info", entries=[
        TabEntry(entry_name="username", label="Username", type="text", required=True, value=item.get("username")),
        TabEntry(entry_name="name", label="Name", type="text", required=True, value=item.get("name")),
    ])

    # Contact section
    contact_section = TabSection(section_name="Contact", entries=[
        TabEntry(entry_name="email", label="Email", type="email", required=True, value=item.get("email")),
    ])

    # Record Info section
    record_info_section = TabSection(section_name="Record Info", entries=[
        TabEntry(entry_name="created_at", label="Created At", type="datetime", value=item.get("created_at")),
        TabEntry(entry_name="updated_at", label="Updated At", type="datetime", value=item.get("updated_at")),
    ])

    # CRISP Score section
    crisp_score_section = TabSection(section_name="CRISP Score", entries=[
        TabEntry(entry_name="crisp", label="CRISP", type="custom", value=item.get("crisp")),
    ])

    # Metadata section
    metadata_section = TabSection(section_name="Metadata", entries=[
        TabEntry(entry_name="created_at", label="Created At", type="readonly", value=item.get("created_at")),
        TabEntry(entry_name="updated_at", label="Updated At", type="readonly", value=item.get("updated_at")),
    ])


    # Tabs
    about_tab = Tab(tab_name="About", sections=[
        basic_info_section,
        contact_section,
        record_info_section,
    ])

    insights_tab = Tab(tab_name="Insights", sections=[
        crisp_score_section,
    ])

    metadata_tab = Tab(tab_name="Metadata", sections=[metadata_section])

    return [about_tab, insights_tab, metadata_tab]
