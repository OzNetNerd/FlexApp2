import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from flask import url_for
from flask_login import current_user, UserMixin
from app.routes.base.tabs import UI_TAB_MAPPING
from app.routes.base.components.tab_builder import create_tabs
from app.utils.app_logging import log_instance_vars

logger = logging.getLogger(__name__)


@dataclass
class Context:
    """Base context class for rendering views with optional dynamic attributes."""

    # When using dataclass inheritance, ALL required parameters without defaults
    # must be defined in the parent class, otherwise child classes will error

    # These fields will be required in ALL child classes
    title: str
    read_only: bool
    current_user: Optional[UserMixin] = None
    item: Optional[Any] = None
    action: Optional[str] = False
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for key, value in self.extra.items():
            setattr(self, key, value)


@dataclass
class TableContext:
    """Context class for rendering table views with full metadata."""

    # Required fields
    page_type: str
    table_config: dict
    table_id: str
    data_url: str
    entity_name: str
    add_url: str
    columns: List[Any]

    # Inherited fields
    title: str = ""
    item: Any = None
    read_only: bool = True
    action: str = "Viewing"
    current_user: Optional[UserMixin] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.title:
            self.title = self.action

        if self.current_user is None:
            self.current_user = current_user

        for key, value in self.extra.items():
            setattr(self, key, value)


@dataclass
class ResourceContext:
    """Holds context data for rendering resource-related views."""

    # Required fields
    model: Any
    blueprint_name: str
    item_dict: dict

    # Optional fields specific to ResourceContext
    autocomplete_fields: list[dict] = field(default_factory=list)
    error_message: str = ""

    # Inherited fields
    title: str = ""
    item: Any = None
    read_only: bool = True
    action: str = "Viewing"
    current_user: Optional[UserMixin] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    # Non-init fields
    tabs: list = field(default_factory=list, init=False)
    item_name: str = field(default="", init=False)
    submit_url: str = field(default="", init=False)
    id: str = field(default="", init=False)
    model_name: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if not self.title:
            self.title = self.action

        if self.current_user is None:
            self.current_user = current_user

        for key, value in self.extra.items():
            setattr(self, key, value)

        self.submit_url = url_for(f"{self.blueprint_name}.create") if not self.read_only else ""
        self.model_name = self.model.__name__
        self.id = str(self.item_dict.get("id", ""))

        logger.info(f"📜 Building '{self.action}' page for '{self.blueprint_name}' blueprint (RO={self.read_only})")

        log_instance_vars(self)

        tab_entries = UI_TAB_MAPPING[self.model_name]
        logger.debug(f"Tab entries for model '{self.model_name}': {tab_entries}")
        self.tabs = create_tabs(item=self.item_dict, tabs=tab_entries)
        logger.debug(f"Tabs created: {self.tabs}")

        for key in ("name", "title", "email", "username"):
            if self.item_dict.get(key):
                self.item_name = self.item_dict[key]
                logger.info(f"ℹ️ item_name set using key '{key}': '{self.item_name}'")
                break
        else:
            self.item_name = self.id
            logger.info(f"item_name defaulted to id: '{self.item_name}'")


class EntityHandler:
    """Handles preparation and validation of dynamic form inputs for web routes."""

    def __init__(self, model: Any, service: Any, json_validator: Any) -> None:
        """
        Initialize the EntityHandler.
        """
        self.model = model
        self.service = service
        self.json_validator = json_validator

    @staticmethod
    def resolve_value(item: Any, name: str) -> str:
        """Resolve a value from a nested object attribute name."""
        try:
            if name == "company_name":
                return item.company.name if item.company else ""
            if name == "crisp":
                return item.crisp_summary if hasattr(item, "crisp_summary") else ""

            for part in name.split("."):
                item = getattr(item, part)
            return item
        except AttributeError:
            logger.warning(f"Unable to resolve value for '{name}'")
            return ""

    @staticmethod
    def validate_create(form_data: Dict[str, Any]) -> List[str]:
        """Validate form data before creating a new record."""
        users = form_data.getlist("users")
        companies = form_data.getlist("companies")

        logger.info(f"👥 Selected user IDs: {users}")
        logger.info(f"🏢 Selected company IDs: {companies}")

        return []

    @staticmethod
    def validate_edit(item: Any, form_data: Dict[str, Any]) -> List[str]:
        """Validate form data before updating an existing record."""
        users = form_data.getlist("users")
        companies = form_data.getlist("companies")

        logger.info(f"✏️ [Edit] Selected user IDs: {users}")
        logger.info(f"✏️ [Edit] Selected company IDs: {companies}")

        return []