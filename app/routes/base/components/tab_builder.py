import logging
import sys
from typing import Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TabEntry:
    entry_name: str
    label: str
    type: str
    required: bool = False
    options: Optional[List[dict[str, Any]]] = None
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
class TabBuilder:
    item: Any
    tab_name: str

    def create_tab(self, tab_sections: List[TabSection]):
        """
        Creates a Tab object with the given tab_name and list of TabSection objects.

        Returns:
            Tab: A Tab object with the given tab_name and sections
        """

        all_tab_sections = tab_sections[:] + [self._metadata_section()]

        logger.info(f"Creating {self.tab_name} tab")
        for tab_section in all_tab_sections:
            logger.debug(f"Finished creating {tab_section.section_name} section: {tab_section}")

        tab = Tab(tab_name=self.tab_name, sections=tab_sections)
        logger.info(f"Finished creating {self.tab_name} section")
        logger.debug(f"{self.tab_name}: {tab}")
        return tab

    def _metadata_section(self):
        section_name = "Metadata"
        metadata_section = TabSection(
            section_name=section_name,
            entries=[
                TabEntry(
                    entry_name="created_at",
                    label="Created At",
                    type="readonly",
                    value=self.item.get("created_at")
                ),
                TabEntry(
                    entry_name="updated_at",
                    label="Updated At",
                    type="readonly",
                    value=self.item.get("updated_at")
                ),
            ]
        )
        return metadata_section