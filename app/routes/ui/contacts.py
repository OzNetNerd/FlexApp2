from app.routes.base.components.form_handler import Tab, TabSection, TabEntry
from typing import List


def get_contact_tabs(item: dict) -> List[Tab]:
    """Returns the list of contact-related tabs with data populated from the item dictionary.

    Args:
        item (dict): Dictionary of field values to populate into TabEntry.value.

    Returns:
        List[Tab]: List of populated Tab objects.
    """
    # Identity section
    identity_section = TabSection(section_name="Identity", entries=[
        TabEntry(entry_name="first_name", label="First Name", type="text", required=True, value=item.get("first_name")),
        TabEntry(entry_name="last_name", label="Last Name", type="text", required=True, value=item.get("last_name")),
    ])

    # Contact Info section
    contact_info_section = TabSection(section_name="Contact Info", entries=[
        TabEntry(entry_name="phone", label="Phone", type="text", value=item.get("phone")),
        TabEntry(entry_name="email", label="Email", type="email", value=item.get("email")),
    ])

    # Company Info section
    company_info_section = TabSection(section_name="Company Info", entries=[
        TabEntry(entry_name="company_name", label="Company", type="text", value=item.get("company_name")),
    ])

    # Record Info section
    record_info_section = TabSection(section_name="Record Info", entries=[
        TabEntry(entry_name="created_at", label="Created At", type="text", value=item.get("created_at")),
        TabEntry(entry_name="updated_at", label="Updated At", type="text", value=item.get("updated_at")),
    ])

    # CRISP Score section
    crisp_score_section = TabSection(section_name="CRISP Score", entries=[
        TabEntry(entry_name="crisp", label="CRISP", type="custom", value=item.get("crisp")),
    ])

    # Tabs
    about_tab = Tab(tab_name="About", sections=[
        identity_section,
        contact_info_section,
        company_info_section,
    ])

    metadata_tab = Tab(tab_name="Metadata", sections=[
        record_info_section,
    ])

    insights_tab = Tab(tab_name="Insights", sections=[
        crisp_score_section,
    ])

    return [about_tab, metadata_tab, insights_tab]
