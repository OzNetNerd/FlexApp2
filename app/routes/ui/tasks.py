from app.routes.base.components.form_handler import Tab, TabSection, TabEntry
from typing import List


def get_task_tabs(item: dict) -> List[Tab]:
    """Returns the list of task-related tabs with data populated from the item dictionary.

    Args:
        item (dict): Dictionary of field values to populate into TabEntry.value.

    Returns:
        List[Tab]: List of populated Tab objects.
    """
    # Task Info section
    task_info_section = TabSection(section_name="Task Info", entries=[
        TabEntry(entry_name="title", label="Title", type="text", required=True, value=item.get("title")),
        TabEntry(entry_name="description", label="Description", type="textarea", value=item.get("description")),
        TabEntry(entry_name="due_date", label="Due Date", type="date", value=item.get("due_date")),
        TabEntry(entry_name="status", label="Status", type="select", required=True, value=item.get("status"), options=[
            {"value": "Pending", "label": "Pending"},
            {"value": "In Progress", "label": "In Progress"},
            {"value": "Completed", "label": "Completed"},
        ]),
        TabEntry(entry_name="priority", label="Priority", type="select", value=item.get("priority"), options=[
            {"value": "Low", "label": "Low"},
            {"value": "Medium", "label": "Medium"},
            {"value": "High", "label": "High"},
        ]),
    ])

    # Linked Entity section
    linked_entity_section = TabSection(section_name="Linked Entity", entries=[
        TabEntry(entry_name="notable_type", label="Linked To (Type)", type="hidden", value=item.get("notable_type", "User")),
        TabEntry(entry_name="notable_id", label="Linked To (ID)", type="hidden", value=item.get("notable_id", "1")),
    ])

    # Tabs
    about_tab = Tab(tab_name="About", sections=[task_info_section])
    details_tab = Tab(tab_name="Details", sections=[linked_entity_section])

    return [about_tab, details_tab]
