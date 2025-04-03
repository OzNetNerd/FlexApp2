import logging
from dataclasses import dataclass
from app.routes.base.components.tab_builder import TabBuilder, TabSection, TabEntry

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

    def _basic_info_section(self):
        section_name = "Basic Info"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="username",
                    label="Username",
                    type="text",
                    required=True,
                    value=self.item.get("username")
                ),
                TabEntry(
                    entry_name="name",
                    label="Name",
                    type="text",
                    required=True,
                    value=self.item.get("name")
                ),
            ]
        )

    def _contact_section(self):
        section_name = "Contact"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="email",
                    label="Email",
                    type="email",
                    required=True,
                    value=self.item.get("email")
                ),
            ]
        )

    def _record_info_section(self):
        section_name = "Record Info"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="created_at",
                    label="Created At",
                    type="datetime",
                    value=self.item.get("created_at")
                ),
                TabEntry(
                    entry_name="updated_at",
                    label="Updated At",
                    type="datetime",
                    value=self.item.get("updated_at")
                ),
            ]
        )

@dataclass
class InsightsTab(TabBuilder):
    tab_name: str = "Insights"

    def __post_init__(self):
        self.section_method_order = [
            self._crisp_score_section,
        ]

    def _crisp_score_section(self):
        section_name = "CRISP Score"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="crisp",
                    label="CRISP",
                    type="custom",
                    value=self.item.get("crisp")
                ),
            ]
        )

@dataclass
class RelationshipsTab(TabBuilder):
    tab_name: str = "Relationships"

    def __post_init__(self):
        self.section_method_order = [
            self._relationships_section,
        ]

    def _relationships_section(self):
        section_name = "Relationships"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="users",
                    label="Users",
                    type="custom",
                    value=self.item.get("users")
                ),
                TabEntry(
                    entry_name="companies",
                    label="Companies",
                    type="custom",
                    value=self.item.get("companies")
                ),
            ]
        )

# Constant list of user-related tabs
USERS_TABS = [AboutTab, InsightsTab, RelationshipsTab]
