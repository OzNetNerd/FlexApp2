import logging
from dataclasses import dataclass, field
from typing import List, Callable, Any
from app.routes.base.components.tab_builder import TabBuilder, TabSection, TabEntry

logger = logging.getLogger(__name__)

@dataclass
class OverviewTab(TabBuilder):
    tab_name: str = "Overview"

    def __post_init__(self):
        self.section_method_order = [
            self._details_section,
            self._pipeline_section,
        ]

        super().__post_init__()

    def _details_section(self):
        section_name = "Details"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="name",
                    label="Name",
                    type="text",
                    required=True,
                    value=self.item.get("name")
                ),
                TabEntry(
                    entry_name="description",
                    label="Description",
                    type="textarea",
                    value=self.item.get("description")
                ),
                TabEntry(
                    entry_name="company.name",
                    label="Company Name",
                    type="text",
                    value=self.item.get("company.name")
                ),
            ]
        )

    def _pipeline_section(self):
        section_name = "Pipeline"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="stage",
                    label="Stage",
                    type="text",
                    required=True,
                    value=self.item.get("stage")
                ),
                TabEntry(
                    entry_name="status",
                    label="Status",
                    type="text",
                    value=self.item.get("status")
                ),
            ]
        )

@dataclass
class DealTab(TabBuilder):
    tab_name: str = "Deal"

    def __post_init__(self):
        self.section_method_order = [
            self._financial_section,
            self._crisp_section,
        ]

        super().__post_init__()

    def _financial_section(self):
        section_name = "Financial"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="value",
                    label="Value",
                    type="number",
                    required=True,
                    value=self.item.get("value")
                ),
            ]
        )

    def _crisp_section(self):
        section_name = "CRISP"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="crisp",
                    label="CRISP",
                    type="string",
                    required=True,
                    value=self.item.get("crisp")
                ),
            ]
        )
# Constant list of opportunity tabs
OPPORTUNITIES_TABS = [OverviewTab, DealTab]
