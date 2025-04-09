import logging
from flask import url_for
from flask_login import current_user, UserMixin
from app.routes.base.tabs import UI_TAB_MAPPING
from app.routes.base.components.tab_builder import create_tabs
from app.utils.app_logging import log_instance_vars
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from app.utils.table_helpers import get_table_id_by_name, get_plural_name


logger = logging.getLogger(__name__)


class BaseContext:
    """Base context class for template rendering with common attributes."""

    def __init__(self, title="", show_navbar=True, read_only=True, **kwargs):
        """
        Initialize the base context with common template variables.

        Args:
            title (str): The page title
            show_navbar (bool): Whether to display the navigation bar
            read_only (bool): Whether the view is in read-only mode
            **kwargs: Additional attributes to set on the context

        Raises:
            ValueError: If neither title nor table_name is provided
        """
        logging.info("Building Base Context")
        if not title and not kwargs.get('table_name'):
            raise ValueError("Either 'title' or 'table_name' must be provided.")

        self.title = title or kwargs['table_name']
        self.current_user = current_user
        self.show_navbar = show_navbar
        self.read_only = read_only

        # Set each keyword argument as an attribute on the instance.
        for key, value in kwargs.items():
            setattr(self, key, value)
            logger.info(f"Set attribute '{key}' = {value}")

    def __repr__(self):
        """Return a detailed string representation of the context."""
        attributes = ", ".join(f"{key}={repr(value)}"
                               for key, value in vars(self).items()
                               if not key.startswith('_'))
        return f"{self.__class__.__name__}({attributes})"

    def __str__(self):
        """Return a user-friendly string representation of the context."""
        return f"{self.__class__.__name__}(title='{self.title}', attrs={len(vars(self))})"

    def to_dict(self):
        """Convert context to dictionary for template rendering."""
        return {key: value for key, value in vars(self).items()
                if not key.startswith('_')}


class SimpleContext(BaseContext):
    """Context class for rendering views with basic attributes."""

    def __init__(self, title: str, show_navbar=True, read_only=True, **kwargs):
        super().__init__(
            title=title,
            show_navbar=show_navbar,
            read_only=read_only,
            **kwargs
        )


class TableContext(SimpleContext):
    """Context class for rendering table views with table-specific attributes."""

    def __init__(self, table_name: str, title: str = "", read_only: bool = True, action: Optional[str] = None,
                 **kwargs):

        # Add table-specific attributes
        self.table_name = table_name
        self.read_only = read_only
        self.action = action

        if title:
            self.title = title
            logger.info(f"title was provided. Set self.title to: {self.title}")

        else:
            self.title = f'{self.action} {self.table_name}' if self.action else self.table_name
            logger.info(f"title was not provided. Set self.title to table name: {self.title}")

        # Initialize the base SimpleContext
        super().__init__(title=self.title, **kwargs)

        lower_table_name = self.table_name.lower()
        logger.info(f'Set lower table name: {lower_table_name}')

        # Set the table_id using the provided table_name
        self.table_id = get_table_id_by_name(self.table_name)
        logger.info(f"Set attribute table_id = {self.table_id} (from {self.table_name})")

        self.data_url = f"/api/{get_plural_name(lower_table_name)}"
        logger.info(f"Set attribute data_url = {self.data_url} (from table_name = {self.table_name})")

    def __str__(self):
        """Return a user-friendly string representation focusing on table attributes."""
        return f"TableContext(table_name='{self.table_name}', table_id={self.table_id}, title='{self.title}')"


class EntityContext(BaseContext):
    """Holds context data for rendering resource-related views."""

    def __init__(self,
                 autocomplete_fields: Optional[List[dict]] = None,
                 error_message: str = "", title: str = "", item: Any = None,
                 read_only: bool = True, action: str = "", name="tba",
                 **kwargs):
        """Initialize the context with proper parent class handling."""
        # Call parent class initializer with all required params
        super().__init__(**kwargs)

        logger.info('initial...')

        # Set instance attributes
        self.autocomplete_fields = autocomplete_fields or []
        self.error_message = error_message
        self.title = title or action
        self.item = item
        self.read_only = read_only
        self.action = action
        self.name = "tba"
        self.current_user = current_user

        # Derived fields initialized in __init__
        self.tabs = []
        self.item_name = ""
        self.submit_url = ""
        self.id = ""
        self.model_name = ""

        # Set derived fields
        self._initialize_derived_fields()

    def _initialize_derived_fields(self):
        """Initialize derived fields."""
        model_name = self.__class__.__name__
        id_value = getattr(self, 'id', "")

        # Get blueprint_name and item_dict from kwargs if available
        blueprint_name = getattr(self, 'blueprint_name', "")
        item_dict = getattr(self, 'item_dict', {})

        self.submit_url = url_for(f"{blueprint_name}.create") if not self.read_only else ""
        self.model_name = model_name
        self.id = str(id_value)

        logger.info(f"📜 Building '{self.action}' page for '{blueprint_name}' blueprint (RO={self.read_only})")
        log_instance_vars(self)

        # Process tab entries
        tab_entries = UI_TAB_MAPPING.get(model_name, [])
        logger.debug(f"Tab entries for model '{model_name}': {tab_entries}")
        self.tabs = create_tabs(item=item_dict, tabs=tab_entries)
        logger.debug(f"Tabs created: {self.tabs}")

        # Set item_name from the first available field
        self.item_name = ""
        for key in ("name", "title", "email", "username"):
            if item_dict.get(key):
                self.item_name = item_dict[key]
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
