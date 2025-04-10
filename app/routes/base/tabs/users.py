import logging
from dataclasses import dataclass
from app.routes.base.components.tab_builder import TabBuilder, TabSection, TabEntry, InsightsTab

logger = logging.getLogger(__name__)


@dataclass
class AboutTab(TabBuilder):
    tab_name: str = "About"

    def __post_init__(self):
        self.section_method_order = [
            self._basic_info_section,
            self._contact_section,
            self._record_info_section,
        ]

        super().__post_init__()

    def _basic_info_section(self):
        section_name = "Basic Info"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="username", label="Username", type="text", required=True, value=self.entity.get("username")),
                TabEntry(entry_name="name", label="Name", type="text", required=True, value=self.entity.get("name")),
            ],
        )

    def _contact_section(self):
        section_name = "Contact"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="email", label="Email", type="email", required=True, value=self.entity.get("email")),
            ],
        )

    def _record_info_section(self):
        section_name = "Record Info"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="created_at", label="Created At", type="datetime", value=self.entity.get("created_at")),
                TabEntry(entry_name="updated_at", label="Updated At", type="datetime", value=self.entity.get("updated_at")),
            ],
        )


@dataclass
class RelationshipsTab(TabBuilder):
    tab_name: str = "Relationships"

    def __post_init__(self):
        self.section_method_order = [
            self._relationships_section,
        ]

        super().__post_init__()

    def _relationships_section(self):
        section_name = "Relationships"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="users", label="Users", type="custom", value=self.entity.get("users")),
                TabEntry(entry_name="companies", label="Companies", type="custom", value=self.entity.get("companies")),
            ],
        )


# Constant list of user-related tabs
USERS_TABS = [AboutTab, InsightsTab, RelationshipsTab]
