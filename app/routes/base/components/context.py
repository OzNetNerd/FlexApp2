import logging
from flask import url_for
from flask_login import current_user
from app.utils.table_helpers import get_page_tabs, get_table_plural_name, get_table_id_by_name
from app.routes.base.components.tab_builder import create_tabs
from app.utils.app_logging import log_instance_vars
from typing import Any, Optional, List

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

    def __init__(self, entity_table_name: str, title: str = "", read_only: bool = True, action: Optional[str] = None, **kwargs):

        # Add table-specific attributes
        self.entity_table_name = entity_table_name
        self.read_only = read_only
        self.action = action

        if title:
            self.title = title
            logger.info(f"title was provided. Set self.title to: {self.title}")

        else:
            self.title = f"{self.action} {self.entity_table_name}" if self.action else self.entity_table_name
            logger.info(f"title was not provided. Set self.title to table name: {self.title}")

        # Initialize the base SimpleContext
        super().__init__(title=self.title, **kwargs)

        lower_entity_table_name = self.entity_table_name.lower()
        logger.info(f"Set lower table name: {lower_entity_table_name}")

        # Set the table_id using the provided entity_table_name
        self.table_id = get_table_id_by_name(self.entity_table_name)
        logger.info(f"Set attribute table_id = {self.table_id} (from {self.entity_table_name})")

        plural_entity_table_name = get_table_plural_name(self.entity_table_name)
        self.data_api_url = f"/api/{plural_entity_table_name}"
        logger.info(f"Set attribute data_url = {self.data_api_url} (from table_name = {self.entity_table_name})")

    def __str__(self):
        """Return a user-friendly string representation focusing on table attributes."""
        return f"TableContext(entity_table_name='{self.entity_table_name}', table_id={self.table_id}, title='{self.title}')"


class EntityContext(BaseContext):
    """Holds context data for rendering resource-related views."""

    def __init__(
        self,
        action: str,
        autocomplete_fields: Optional[List[dict]] = None,
        error_message: str = "",
        title: str = "",
        entity: Any = None,
        read_only: bool = True,
        entity_table_name: str = "",
        entity_id: Any = None,
        **kwargs,
    ):
        """Initialize the context with proper parent class handling."""
        # Call parent class initializer with all required params
        super().__init__(title=title, read_only=read_only, **kwargs)

        # Set instance attributes
        self.autocomplete_fields = autocomplete_fields or []
        self.error_message = error_message
        self.title = title or action
        self.entity = entity
        self.read_only = read_only
        self.action = action
        self.name = "tba"
        self.current_user = current_user
        self.entity_table_name = entity_table_name  # Store table_name
        self.entity_id = entity_id    # Store entity_id

        # Derived fields initialized in __init__
        self.tabs = []
        self.entity_name = ""
        self.submit_url = ""
        self.id = ""
        self.model_name = ""

        # Set derived fields
        self._initialize_derived_fields()

    def __str__(self):
        """Return a user-friendly string representation focusing on key entity attributes."""
        return f"EntityContext(model='{self.model_name}', action='{self.action}', entity='{self.entity_name}')"

    def __repr__(self):
        """Return a detailed string representation of the entity context."""
        # Include important fields first, then all others
        primary_attrs = {
            "model_name": self.model_name,
            "action": self.action,
            "entity_name": self.entity_name,
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
        if isinstance(self.entity, dict) and self.entity:
            other_attrs["entity"] = f"[{len(self.entity)} keys]"
        elif self.entity:
            other_attrs["entity"] = f"<{type(self.entity).__name__}>"

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
        # Use entity_table_name for model_name if available, otherwise use class name
        self.model_name = self.entity_table_name or self.__class__.__name__
        self.id = str(getattr(self, "entity_id", ""))

        # Get blueprint_name from kwargs if available
        blueprint_name = getattr(self, "blueprint_name", "")

        # Create entity_dict from entity if available
        entity_dict = {}
        if self.entity:
            # Convert entity to dictionary if it's not already
            if isinstance(self.entity, dict):
                entity_dict = self.entity
            elif hasattr(self.entity, "__dict__"):
                # For ORM models or objects with __dict__
                entity_dict = {k: v for k, v in self.entity.__dict__.items()
                           if not k.startswith('_')}
            elif hasattr(self.entity, "to_dict"):
                # For objects with to_dict method
                entity_dict = self.entity.to_dict()
        # Fallback to self.entity if it's a dict
        elif isinstance(self.entity, dict):
            entity_dict = self.entity

        self.submit_url = url_for(f"{blueprint_name}.create") if not self.read_only else ""

        logger.info(f"📜 Building '{self.action}' page for '{blueprint_name}' blueprint (RO={self.read_only})")
        instance_details = "EntityContext (_initialize_derived_fields)"
        log_instance_vars(instance_details, self)

        tab_entries = get_page_tabs(self.model_name)
        logger.debug(f"Tab entries for model '{self.model_name}': {tab_entries}")
        self.tabs = create_tabs(entity=entity_dict, tabs=tab_entries)
        logger.debug(f"Tabs created: {self.tabs}")

        # Set entity_name from the first available field
        self.entity_name = ""
        for key in ("name", "title", "email", "username"):
            if entity_dict.get(key):
                self.entity_name = entity_dict[key]
                logger.info(f"ℹ️ entity_name set using key '{key}': '{self.entity_name}'")
                break
        else:
            self.entity_name = self.id
            logger.info(f"entity_name defaulted to id: '{self.entity_name}'")

#
# @dataclass
# class BaseContextConfig:
#     table_name: str
#     action: str
#     title: Optional[str] = None
#
#     def __post_init__(self):
#         # If title is not provided, set it to 'action + table_name'
#         if not self.title:
#             self.title = f"{self.action} {self.table_name}"
#
# # TableContextConfig class for the 'index' context
# @dataclass
# class TableContextConfig(BaseContextConfig):
#     read_only: bool = True
#
# # EntityContextConfig class for 'create', 'view', and 'edit' contexts
# @dataclass
# class EntityContextConfig(BaseContextConfig):
#     read_only: bool = field(init=False)  # Will be set in __post_init__
#     id: Optional[int] = None
#     entity: Optional[object] = None  # Adjust based on your actual entity type
#
#     def __post_init__(self):
#         super().__post_init__()  # Call parent class __post_init__
#         # Set read_only based on action
#         if self.action in ['create', 'edit']:
#             self.read_only = False  # Write actions
#         else:
#             self.read_only = True  # Read-only actions