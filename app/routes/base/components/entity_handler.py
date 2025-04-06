import logging
from flask import url_for
from flask_login import current_user, UserMixin
from app.routes.base.tabs import UI_TAB_MAPPING
from app.routes.base.components.tab_builder import create_tabs
from app.utils.app_logging import log_instance_vars
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from app.utils.table_helpers import get_table_id_by_name


logger = logging.getLogger(__name__)

class BaseContext:
    def __init__(self, **kwargs):

        # avoid IDE error
        self.table_name = ""

        # Set each keyword argument as an attribute on the instance.
        for key, value in kwargs.items():
            setattr(self, key, value)
            logger.info(f"Set attribute '{key}' = {value}")

        # Set the table_id using the provided table_name
        self.table_id = get_table_id_by_name(self.table_name)
        logger.info(f"Set attribute table_id = {self.table_id} (from {self.table_name} = {self.table_name})")

        self.data_url = f"{self.table_name}/data"
        logger.info(f"Set attribute data_url = {self.data_url} (from table_name = {self.table_name})")


@dataclass
class SimpleContext(BaseContext):
    """Context class for rendering views with optional dynamic attributes."""

    def __init__(self, title: str, table_name: str, read_only: bool = True, action: Optional[str] = False, **kwargs):
        super().__init__(
            title=title,
            table_name=table_name,
            read_only=read_only,
            action=action,
            current_user=current_user,
            show_navbar=True,
            **kwargs
        )

@dataclass
class ResourceContext(BaseContext):
    """Holds context data for rendering resource-related views."""

    model: Any
    blueprint_name: str
    item_dict: dict

    autocomplete_fields: List[dict] = field(default_factory=list)
    error_message: str = ""

    title: str = ""
    item: Any = None
    read_only: bool = True
    action: str = "Viewing"
    current_user: Optional['UserMixin'] = None  # Replace if needed

    tabs: list = field(default_factory=list, init=False)
    item_name: str = field(default="", init=False)
    submit_url: str = field(default="", init=False)
    id: str = field(default="", init=False)
    model_name: str = field(default="", init=False)

    def __init__(self, model: Any, blueprint_name: str, item_dict: dict,
                 autocomplete_fields: Optional[List[dict]] = None,
                 error_message: str = "", title: str = "", item: Any = None,
                 read_only: bool = True, action: str = "Viewing",
                 current_user: Optional['UserMixin'] = None, **kwargs):
        if not title:
            title = action
        if current_user is None:
            current_user = current_user  # fallback to global if needed

        super().__init__(
            model=model,
            blueprint_name=blueprint_name,
            item_dict=item_dict,
            autocomplete_fields=autocomplete_fields or [],
            error_message=error_message,
            title=title,
            item=item,
            read_only=read_only,
            action=action,
            current_user=current_user,
            **kwargs
        )

        self.submit_url = url_for(f"{self.blueprint_name}.create") if not read_only else ""
        self.model_name = model.__name__
        self.id = str(item_dict.get("id", ""))

        logger.info(f"📜 Building '{action}' page for '{blueprint_name}' blueprint (RO={read_only})")
        log_instance_vars(self)

        tab_entries = UI_TAB_MAPPING[self.model_name]
        logger.debug(f"Tab entries for model '{self.model_name}': {tab_entries}")
        self.tabs = create_tabs(item=item_dict, tabs=tab_entries)
        logger.debug(f"Tabs created: {self.tabs}")

        for key in ("name", "title", "email", "username"):
            if item_dict.get(key):
                self.item_name = item_dict[key]
                logger.info(f"ℹ️ item_name set using key '{key}': '{self.item_name}'")
                break
        else:
            self.item_name = self.id
            logger.info(f"item_name defaulted to id: '{self.item_name}'")


@dataclass
class TableContext(BaseContext):
    """Context class for rendering table views with full metadata."""

    page_type: str
    table_config: dict
    table_id: str
    data_url: str
    entity_name: str
    add_url: str
    columns: List[Any]

    title: str = ""
    item: Any = None
    read_only: bool = True
    action: str = "Viewing"
    current_user: Optional['UserMixin'] = None  # Replace if needed

    def __init__(self, page_type: str, table_config: dict, table_id: str, data_url: str,
                 entity_name: str, add_url: str, columns: List[Any], title: str = "",
                 item: Any = None, read_only: bool = True, action: str = "Viewing",
                 current_user: Optional['UserMixin'] = None, **kwargs):
        if not title:
            title = action
        if current_user is None:
            current_user = current_user  # fallback to global if needed

        super().__init__(
            page_type=page_type,
            table_config=table_config,
            table_id=table_id,
            data_url=data_url,
            entity_name=entity_name,
            add_url=add_url,
            columns=columns,
            title=title,
            item=item,
            read_only=read_only,
            action=action,
            current_user=current_user,
            **kwargs
        )


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
