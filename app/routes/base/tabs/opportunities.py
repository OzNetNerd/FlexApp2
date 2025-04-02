from app.routes.base.components.tab_builder import Tab, TabSection, TabEntry
from typing import List


def get_opportunity_tabs(item: dict) -> List[Tab]:
    """Returns the list of opportunity-related tabs with data populated from the item dictionary.

    Args:
        item (dict): Dictionary of field values to populate into TabEntry.value.

    Returns:
        List[Tab]: List of populated Tab objects.
    """
    # Details section
    details_section = TabSection(section_name="Details", entries=[
        TabEntry(entry_name="name", label="Name", type="text", required=True, value=item.get("name")),
        TabEntry(entry_name="description", label="Description", type="textarea", value=item.get("description")),
        TabEntry(entry_name="company.name", label="Company Name", type="text", value=item.get("company.name")),
    ])

    # Pipeline section
    pipeline_section = TabSection(section_name="Pipeline", entries=[
        TabEntry(entry_name="stage", label="Stage", type="text", required=True, value=item.get("stage")),
        TabEntry(entry_name="status", label="Status", type="text", value=item.get("status")),
    ])

    # Financial section
    financial_section = TabSection(section_name="Financial", entries=[
        TabEntry(entry_name="value", label="Value", type="number", required=True, value=item.get("value")),
    ])

    # CRISP section
    crisp_section = TabSection(section_name="CRISP", entries=[
        TabEntry(entry_name="crisp", label="CRISP", type="string", required=True, value=item.get("crisp")),
    ])

    # Metadata section
    metadata_section = TabSection(section_name="Metadata", entries=[
        TabEntry(entry_name="created_at", label="Created At", type="readonly", value=item.get("created_at")),
        TabEntry(entry_name="updated_at", label="Updated At", type="readonly", value=item.get("updated_at")),
    ])

    # Tabs
    overview_tab = Tab(tab_name="Overview", sections=[details_section, pipeline_section])
    deal_tab = Tab(tab_name="Deal", sections=[financial_section, crisp_section])
    metadata_tab = Tab(tab_name="Metadata", sections=[metadata_section])

    return [overview_tab, deal_tab, metadata_tab]
