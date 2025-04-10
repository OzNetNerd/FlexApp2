import logging
from dataclasses import dataclass
from app.routes.web.components.tab_builder import TabBuilder, TabSection, TabEntry

logger = logging.getLogger(__name__)


@dataclass
class AboutTab(TabBuilder):
    tab_name: str = "About"

    def __post_init__(self):
        self.section_method_order = [
            self._task_info_section,
        ]

        super().__post_init__()

    def _task_info_section(self):
        section_name = "Task Info"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="title", label="Title", type="text", required=True, value=self.entity.get("title")),
                TabEntry(entry_name="description", label="Description", type="textarea", value=self.entity.get("description")),
                TabEntry(entry_name="due_date", label="Due Date", type="date", value=self.entity.get("due_date")),
                TabEntry(
                    entry_name="status",
                    label="Status",
                    type="select",
                    required=True,
                    value=self.entity.get("status"),
                    options=[
                        {"value": "Pending", "label": "Pending"},
                        {"value": "In Progress", "label": "In Progress"},
                        {"value": "Completed", "label": "Completed"},
                    ],
                ),
                TabEntry(
                    entry_name="priority",
                    label="Priority",
                    type="select",
                    value=self.entity.get("priority"),
                    options=[
                        {"value": "Low", "label": "Low"},
                        {"value": "Medium", "label": "Medium"},
                        {"value": "High", "label": "High"},
                    ],
                ),
            ],
        )


@dataclass
class DetailsTab(TabBuilder):
    tab_name: str = "Details"

    def __post_init__(self):
        self.section_method_order = [
            self._linked_entity_section,
        ]

        super().__post_init__()

    def _linked_entity_section(self):
        section_name = "Linked Entity"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="notable_type", label="Linked To (Type)", type="hidden", value=self.entity.get("notable_type", "User")),
                TabEntry(entry_name="notable_id", label="Linked To (ID)", type="hidden", value=self.entity.get("notable_id", "1")),
            ],
        )


# Constant list of task-related tabs
TASKS_TABS = [AboutTab, DetailsTab]
