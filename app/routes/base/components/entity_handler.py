import logging
from typing import Any, Dict, List
from dataclasses import dataclass, field
from flask import url_for
from flask_login import current_user
from app.routes.base.tabs import UI_TAB_MAPPING
from app.routes.base.components.tab_builder import create_tabs
from app.utils.app_logging import log_instance_vars

logger = logging.getLogger(__name__)


@dataclass
class Context:
    """Base context class for rendering views with optional dynamic attributes.

    This class is commonly used to pass data into templates, including a title,
    the main item being viewed or edited, and whether the view is read-only.
    Arbitrary extra fields can be injected via the `extra` dictionary.

    Attributes:
        title: Optional title to be displayed in the view.
        item: Optional object (e.g., model instance or dict) being viewed.
        read_only: Whether the view is in read-only mode.
        extra: Dictionary of additional dynamic fields to attach to this instance.
    """

    title: str = ""
    item: Any = None
    read_only: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)
    action: str = "Viewing"

    def __post_init__(self):
        if not self.title:
            self.title = self.action

        for key, value in self.extra.items():
            setattr(self, key, value)


@dataclass
class TableContext:
    """Context class for rendering table views with full metadata.

    Used to render data tables in the UI, including configuration,
    data source URL, table layout, and metadata about the table and entity.

    Attributes:
        page_type: Type of page being rendered (e.g. 'list', 'dashboard').
        table_config: Configuration dictionary for the table (columns, filters, etc.).
        table_id: Unique identifier for the table.
        data_url: Endpoint that returns table data in JSON format.
        entity_name: Name of the entity being displayed (e.g., 'users').
        add_url: URL to the form for adding new entries.
        columns: List of columns to be displayed in the table.
        title: Optional page or section title.
        item: Optional object (e.g., model instance or dict) tied to the context.
        read_only: Whether the table is displayed in read-only mode.
        extra: Dictionary of additional dynamic fields to attach to this instance.
    """

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
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for key, value in self.extra.items():
            setattr(self, key, value)


@dataclass
class ResourceContext:
    """Holds context data for rendering resource-related views (read-only or editable).

    This context is used to initialize UI tabs, configure submission URLs, and
    extract metadata like item names and model names for use in rendering.

    Attributes:
        model: The data model class associated with the item.
        blueprint_name: Flask blueprint name used to build the create URL.
        item_dict: Dictionary representing the item (e.g. a DB row).
        title: Optional title for the context.
        autocomplete_fields: Fields used for autocomplete functionality.
        error_message: Error message to be shown in the UI.
        item: Optional raw object representation of the item.
        read_only: Indicates if the context is read-only.
        extra: Additional dynamic attributes to attach to the instance.
        tabs: List of tab objects for the UI.
        current_user: The current logged-in user.
        item_name: Display name of the item (e.g. "Jessie Smith").
        submit_url: URL to submit the form (blank if read-only).
        id: ID of the item as a string.
        model_name: Name of the model class.
        action: Optional title for the context.
    """

    model: Any
    blueprint_name: str
    item_dict: dict
    title: str = ""
    autocomplete_fields: list[dict] = field(default_factory=list)
    error_message: str = ""
    item: Any = None
    read_only: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)

    tabs: list = field(default_factory=list, init=False)
    current_user: Any = field(default=None, init=False)
    item_name: str = field(default="", init=False)
    submit_url: str = field(default="", init=False)
    id: str = field(default="", init=False)
    model_name: str = field(default="", init=False)
    action: str = "Viewing"

    def __post_init__(self) -> None:
        self.current_user = current_user

        self.submit_url = url_for(f"{self.blueprint_name}.create") if not self.read_only else ""
        self.model_name = self.model.__name__
        self.id = str(self.item_dict.get("id", ""))

        if self.extra:
            for key, value in self.extra.items():
                setattr(self, key, value)

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
    """Handles preparation and validation of dynamic form inputs for web routes.

    This class is typically used in routes where SQLAlchemy models are created or edited
    through forms. It also provides utility functions for resolving nested attributes and
    logging selected relationships such as users or companies.
    """

    def __init__(self, model: Any, service: Any, json_validator: Any) -> None:
        """
        Initialize the EntityHandler.

        Args:
            model: SQLAlchemy model class being managed.
            service: Service object responsible for performing CRUD operations.
            json_validator: Utility class or function for validating JSON payloads.
        """
        self.model = model
        self.service = service
        self.json_validator = json_validator

    @staticmethod
    def resolve_value(item: Any, name: str) -> str:
        """Resolve a value from a nested object attribute name.

        Supports dot notation (e.g. "company.name") and special handling for known cases
        like "company_name" and "crisp".

        Args:
            item: An object with attributes to be resolved (usually a model instance).
            name: Dot-separated path or alias to the value.

        Returns:
            str: The resolved value as a string, or empty string if resolution fails.
        """
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
        """Validate form data before creating a new record.

        Logs selected user and company IDs from the form input.

        Args:
            form_data: Dictionary-like form input (e.g., from Flask `request.form`).

        Returns:
            List[str]: A list of validation error messages (empty if valid).
        """
        users = form_data.getlist("users")
        companies = form_data.getlist("companies")

        logger.info(f"👥 Selected user IDs: {users}")
        logger.info(f"🏢 Selected company IDs: {companies}")

        return []

    @staticmethod
    def validate_edit(item: Any, form_data: Dict[str, Any]) -> List[str]:
        """Validate form data before updating an existing record.

        Logs selected user and company IDs from the form input.

        Args:
            item: Existing SQLAlchemy model instance being edited.
            form_data: Dictionary-like updated form input.

        Returns:
            List[str]: A list of validation error messages (empty if valid).
        """
        users = form_data.getlist("users")
        companies = form_data.getlist("companies")

        logger.info(f"✏️ [Edit] Selected user IDs: {users}")
        logger.info(f"✏️ [Edit] Selected company IDs: {companies}")

        return []
