import logging
from flask import url_for
from flask_login import current_user
from app.routes.base.tabs import UI_TAB_MAPPING
from app.routes.base.components.tab_builder import create_tabs
from app.utils.app_logging import log_instance_vars
from typing import Any, Optional, List
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
        if not title and not kwargs.get("table_name"):
            raise ValueError("Either 'title' or 'table_name' must be provided.")

        self.title = title or kwargs["table_name"]
        self.current_user = current_user
        self.show_navbar = show_navbar
        self.read_only = read_only

        # Set each keyword argument as an attribute on the instance.
        for key, value in kwargs.items():
            setattr(self, key, value)
            logger.info(f"Set attribute '{key}' = {value}")

    def __repr__(self):
        """Return a detailed string representation of the context."""
        attributes = ", ".join(f"{key}={repr(value)}" for key, value in vars(self).items() if not key.startswith("_"))
        return f"{self.__class__.__name__}({attributes})"

    def __str__(self):
        """Return a user-friendly string representation of the context."""
        return f"{self.__class__.__name__}(title='{self.title}', attrs={len(vars(self))})"

    def to_dict(self):
        """Convert context to dictionary for template rendering."""
        return {key: value for key, value in vars(self).items() if not key.startswith("_")}


class SimpleContext(BaseContext):
    """Context class for rendering views with basic attributes."""

    def __init__(self, title: str, show_navbar=True, read_only=True, **kwargs):
        super().__init__(title=title, show_navbar=show_navbar, read_only=read_only, **kwargs)


class TableContext(SimpleContext):
    """Context class for rendering table views with table-specific attributes."""

    def __init__(self, table_name: str, title: str = "", read_only: bool = True, action: Optional[str] = None, **kwargs):

        # Add table-specific attributes
        self.table_name = table_name
        self.read_only = read_only
        self.action = action

        if title:
            self.title = title
            logger.info(f"title was provided. Set self.title to: {self.title}")

        else:
            self.title = f"{self.action} {self.table_name}" if self.action else self.table_name
            logger.info(f"title was not provided. Set self.title to table name: {self.title}")

        # Initialize the base SimpleContext
        super().__init__(title=self.title, **kwargs)

        lower_table_name = self.table_name.lower()
        logger.info(f"Set lower table name: {lower_table_name}")

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

    def __init__(
        self,
        autocomplete_fields: Optional[List[dict]] = None,
        error_message: str = "",
        title: str = "",
        item: Any = None,
        read_only: bool = True,
        action: str = "",
        table_name: str = "",  # Add table_name parameter
        entity: Any = None,    # Add entity parameter
        entity_id: Any = None, # Add entity_id parameter
        **kwargs,
    ):
        """Initialize the context with proper parent class handling."""
        # Call parent class initializer with all required params
        super().__init__(title=title, read_only=read_only, **kwargs)

        # Set instance attributes
        self.autocomplete_fields = autocomplete_fields or []
        self.error_message = error_message
        self.title = title or action
        self.item = item
        self.read_only = read_only
        self.action = action
        self.name = "tba"
        self.current_user = current_user
        self.table_name = table_name  # Store table_name
        self.entity = entity          # Store entity
        self.entity_id = entity_id    # Store entity_id

        # Derived fields initialized in __init__
        self.tabs = []
        self.item_name = ""
        self.submit_url = ""
        self.id = ""
        self.model_name = ""

        # Set derived fields
        self._initialize_derived_fields()

    def __str__(self):
        """Return a user-friendly string representation focusing on key entity attributes."""
        return f"EntityContext(model='{self.model_name}', action='{self.action}', item='{self.item_name}')"

    def __repr__(self):
        """Return a detailed string representation of the entity context."""
        # Include important fields first, then all others
        primary_attrs = {
            "model_name": self.model_name,
            "action": self.action,
            "item_name": self.item_name,
            "read_only": self.read_only,
            "id": self.id,
        }

        # Format primary attributes
        primary_str = ", ".join(f"{key}={repr(value)}" for key, value in primary_attrs.items())

        # Get all other attributes (excluding private ones)
        other_attrs = {key: value for key, value in vars(self).items() if not key.startswith("_") and key not in primary_attrs}

        # Add summary of complex attributes
        if self.autocomplete_fields:
            other_attrs["autocomplete_fields"] = f"[{len(self.autocomplete_fields)} fields]"
        if self.tabs:
            other_attrs["tabs"] = f"[{len(self.tabs)} tabs]"
        if isinstance(self.item, dict) and self.item:
            other_attrs["item"] = f"[{len(self.item)} keys]"
        elif self.item:
            other_attrs["item"] = f"<{type(self.item).__name__}>"

        # Format other attributes
        other_str = ", ".join(f"{key}={repr(value)}" for key, value in other_attrs.items())

        # Combine both parts
        full_repr = f"EntityContext({primary_str}"
        if other_str:
            full_repr += f", {other_str}"
        full_repr += ")"

        return full_repr

    def _initialize_derived_fields(self):
        """Initialize derived fields."""
        # Use table_name for model_name if available, otherwise use class name
        self.model_name = self.table_name or self.__class__.__name__
        self.id = str(getattr(self, "entity_id", ""))

        # Get blueprint_name from kwargs if available
        blueprint_name = getattr(self, "blueprint_name", "")

        # Create item_dict from entity if available
        item_dict = {}
        if self.entity:
            # Convert entity to dictionary if it's not already
            if isinstance(self.entity, dict):
                item_dict = self.entity
            elif hasattr(self.entity, "__dict__"):
                # For ORM models or objects with __dict__
                item_dict = {k: v for k, v in self.entity.__dict__.items()
                           if not k.startswith('_')}
            elif hasattr(self.entity, "to_dict"):
                # For objects with to_dict method
                item_dict = self.entity.to_dict()
        # Fallback to self.item if it's a dict
        elif isinstance(self.item, dict):
            item_dict = self.item

        self.submit_url = url_for(f"{blueprint_name}.create") if not self.read_only else ""

        logger.info(f"📜 Building '{self.action}' page for '{blueprint_name}' blueprint (RO={self.read_only})")
        instance_details = "EntityContext (_initialize_derived_fields)"
        log_instance_vars(instance_details, self)

        # Process tab entries using table_name to lookup in UI_TAB_MAPPING
        tab_entries = UI_TAB_MAPPING.get(self.model_name, [])
        logger.debug(f"Tab entries for model '{self.model_name}': {tab_entries}")
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