import logging
from typing import Any, List, Optional, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TabEntry:
    entry_name: str
    label: str
    type: str
    required: bool = False
    options: Optional[List[Any]] = None
    default: Optional[Any] = None
    value: Optional[Any] = None


@dataclass
class TabSection:
    section_name: str
    entries: List[TabEntry] = field(default_factory=list)

@dataclass
class Tab:
    tab_name: str
    sections: List[TabSection] = field(default_factory=list)

class TabBuilder:
    item: Any
    tab_name: str
    # order the sections will be displayed
    section_method_order: List[Callable]

    def _metadata_section(self):
        section_name = "Metadata"
        metadata_section = TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="created_at", label="Created At", type="readonly", value=self.item.get("created_at")),
                TabEntry(entry_name="updated_at", label="Updated At", type="readonly", value=self.item.get("updated_at")),
            ]
        )
        return metadata_section

    def create_tab(self):
        """
        Creates a Tab object with the given tab_name and list of TabSection objects.
        """
        # Call each section method to get the actual TabSection objects
        sections = [method() for method in self.section_method_order]
        tab = Tab(tab_name=self.tab_name, sections=sections)
        logger.debug(f"{self.tab_name} tabbing: {tab}")
        return tab