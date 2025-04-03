import logging
from typing import Any, List, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC

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

@dataclass
class TabBuilder(ABC):
    item: Any
    tab_name: str
    include_metadata: bool = True
    section_method_order: List[Callable] = field(default_factory=list, init=False)

    def __post_init__(self):
        if self.include_metadata:
            self.section_method_order.append(self._metadata_section)

    def _metadata_section(self) -> TabSection:
        section_name = "Metadata"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="created_at", label="Created At", type="readonly", value=self.item.get("created_at")),
                TabEntry(entry_name="updated_at", label="Updated At", type="readonly", value=self.item.get("updated_at")),
            ]
        )

    def create_tab(self) -> Tab:
        sections = [method() for method in self.section_method_order]
        tab = Tab(tab_name=self.tab_name, sections=sections)
        logger.debug(f"{self.tab_name} tabbing: {tab}")
        return tab

def create_tabs(item: Any, tabs: List[Callable[[Any], TabBuilder]]) -> List[Tab]:
    grouped_tabs = []
    for tab_class in tabs:
        tab_obj = tab_class(item)
        logger.info(f'Creating tab: {tab_obj.tab_name}')
        tab_entry = tab_obj.create_tab()
        grouped_tabs.append(tab_entry)
    return grouped_tabs