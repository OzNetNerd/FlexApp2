import logging
from typing import Any, List, Optional, Callable, Set, Union
from dataclasses import dataclass, field
from abc import ABC
from enum import Enum, auto

from app.utils.app_logging import log_instance_vars

logger = logging.getLogger(__name__)


class PageType(Enum):
    VIEW = "view"
    CREATE = "create"
    EDIT = "edit"


@dataclass
class TabVisibility:
    # Use one of these two options:
    show_only_on: Set[PageType] = field(default_factory=set)  # Include tab ONLY on these pages
    hide_only_on: Set[PageType] = field(default_factory=set)  # Include tab on ALL EXCEPT these pages

    def is_visible(self, current_page: PageType) -> bool:
        # If both are empty, show on all pages
        if not self.show_only_on and not self.hide_only_on:
            return True

        # If show_only_on is set, check if current page is in that list
        if self.show_only_on:
            return current_page in self.show_only_on

        # If hide_only_on is set, check if current page is NOT in that list
        if self.hide_only_on:
            return current_page not in self.hide_only_on

        return True  # Default to visible if no rules match


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
    visibility: TabVisibility = field(default_factory=TabVisibility)


@dataclass
class TabBuilder(ABC):
    entity: Any
    tab_name: str
    section_method_order: List[Callable] = field(default_factory=list, init=False)
    visibility: TabVisibility = field(default_factory=TabVisibility)

    def __post_init__(self):
        instance_details = "TabBuilder (__post_init__)"
        log_instance_vars(instance_details, self, exclude=["entity"])

    def create_tab(self) -> Tab:
        sections = [method() for method in self.section_method_order]
        tab = Tab(tab_name=self.tab_name, sections=sections, visibility=self.visibility)
        logger.debug(f"{self.tab_name} tabbing: {tab}")
        return tab


@dataclass
class InsightsTab(TabBuilder):
    tab_name: str = "Insights"

    def __post_init__(self):
        # Set visibility to only show on view page
        self.visibility = TabVisibility(show_only_on={PageType.VIEW})

        self.section_method_order = [
            self._crisp_score_section,
        ]

        super().__post_init__()

    def _crisp_score_section(self):
        section_name = "CRISP Score"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="crisp", label="CRISP", type="custom", value=self.entity.get("crisp")),
            ],
        )

@dataclass
class MetadataTab(TabBuilder):
    tab_name: str = "Metadata"

    def __post_init__(self):
        # Show metadata only on view page
        self.visibility = TabVisibility(show_only_on={PageType.VIEW})
        self.section_method_order = [
            self._metadata_section,
        ]

    def _metadata_section(self):
        section_name = "Metadata"
        return TabSection(
            section_name=section_name,
            entries=[
                TabEntry(entry_name="created_at", label="Created At", type="readonly",
                         value=self.entity.get("created_at")),
                TabEntry(entry_name="updated_at", label="Updated At", type="readonly",
                         value=self.entity.get("updated_at")),
            ],
        )


from flask import request


def create_tabs(entity: Any, tabs: List[Callable], current_page=None, add_metadata_tab=True) -> List[Tab]:
    # Auto-detect current page from request if not provided
    if current_page is None:
        # Extract page type from endpoint name
        endpoint = request.endpoint if hasattr(request, 'endpoint') else ""
        if endpoint.endswith('.view'):
            current_page = PageType.VIEW
        elif endpoint.endswith('.edit'):
            current_page = PageType.EDIT
        elif endpoint.endswith('.create'):
            current_page = PageType.CREATE
        else:
            # Default to showing all tabs if we can't determine the page type
            logger.warning(f"Could not determine page type from endpoint: {endpoint}")
            current_page = None

    logger.info(f"ℹ️ About to start creating tabs for UI on {current_page.value if current_page else 'unknown'} page")

    if add_metadata_tab:
        all_tabs = list(tabs) + ([MetadataTab])
        logger.info("ℹ️ Add 'metadata' option is enabled. Will add the tab to the UI if visible for this page")
    else:
        logger.info("ℹ️ Add 'metadata' option is disabled. Will NOT add the tab to the UI")
        all_tabs = tabs

    grouped_tabs = []
    for tab_class in all_tabs:
        tab_obj = tab_class(entity)

        # Only check visibility if we know the current page
        if current_page is None or tab_obj.visibility.is_visible(current_page):
            logger.info(f"📂 Creating tab: {tab_obj.tab_name}")
            tab_entry = tab_obj.create_tab()
            grouped_tabs.append(tab_entry)
        else:
            logger.info(f"🚫 Skipping tab: {tab_obj.tab_name} - not visible on {current_page.value} page")

    logger.info(f" Successfully added {len(grouped_tabs)} tabs")
    return grouped_tabs