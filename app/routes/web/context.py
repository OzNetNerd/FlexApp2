from typing import Any, List, Optional

from flask import url_for
from flask_login import current_user

from app.utils.app_logging import get_logger, log_instance_vars
from app.utils.table_helpers import get_table_id_by_name, get_table_plural_name

logger = get_logger()


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
        instance_details = "BaseContext (__init__)"
        log_instance_vars(instance_details, self)

        if not title and not kwargs.get("entity_table_name"):
            raise ValueError("Either 'title' or 'entity_table_name' must be provided.")

        self.title = title or kwargs["table_name"]
        self.current_user = current_user
        self.show_navbar = show_navbar
        self.read_only = read_only

        # Set each keyword argument as an attribute on the instance.
        for key, value in kwargs.items():
            setattr(self, key, value)
            logger.info(f"Set attribute {key!r} = {value!r}")

    def __repr__(self):
        """Return a detailed string representation of the context."""
        attributes = ", ".join(f"{key}={repr(value)}" for key, value in vars(self).items() if not key.startswith("_"))
        return f"{self.__class__.__name__}({attributes})"

    def __str__(self):
        """Return a user-friendly string representation of the context."""
        return f"{self.__class__.__name__}(title={self.title!r}, attrs={len(vars(self))})"

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
        self.entity_table_name = entity_table_name
        self.read_only = read_only
        self.action = action

        if title:
            self.title = title
            logger.info(f"title was provided. Set self.title to: {self.title!r}")
        else:
            self.title = f"{self.action} {self.entity_table_name}" if self.action else self.entity_table_name
            logger.info(f"title was not provided. Set self.title to table name: {self.title!r}")

        super().__init__(title=self.title, **kwargs)

        lower_entity_table_name = self.entity_table_name.lower()
        logger.info(f"Set lower table name: {lower_entity_table_name!r}")

        self.table_id = get_table_id_by_name(self.entity_table_name)
        logger.info(f"Set attribute table_id = {self.table_id!r} (from {self.entity_table_name!r})")

        plural_entity_table_name = get_table_plural_name(self.entity_table_name)
        self.data_api_url = f"/api/{plural_entity_table_name}"
        logger.info(f"Set attribute data_url = {self.data_api_url!r} (from table_name = {self.entity_table_name!r})")

    def __str__(self):
        """Return a user-friendly string representation focusing on table attributes."""
        return f"TableContext(entity_table_name={self.entity_table_name!r}, table_id={self.table_id}, title={self.title!r})"


class EntityContext(BaseContext):
    """Holds context data for rendering resource-related views."""

    def __init__(
        self,
        action: str,
        entity: Any,
        autocomplete_fields: Optional[List[dict]] = None,
        error_message: str = "",
        title: str = "",
        read_only: bool = True,
        entity_table_name: str = "",
        entity_id: Any = None,
        **kwargs,
    ):
        super().__init__(
            title=title, show_navbar=True, read_only=read_only,
            entity_table_name=entity_table_name, table_name=entity_table_name, **kwargs
        )

        self.autocomplete_fields = autocomplete_fields or []
        self.error_message = error_message
        self.title = title or action
        self.entity = entity
        self.read_only = read_only
        self.action = action
        self.name = "tba"
        self.current_user = current_user
        self.entity_table_name = entity_table_name
        self.entity_id = entity_id

        self.tabs = []
        self.entity_name = ""
        self.submit_url = ""
        self.id = ""
        self.model_name = ""

        self._initialize_derived_fields()

    def __str__(self):
        return f"EntityContext(model={self.model_name!r}, action={self.action!r}, entity={self.entity_name!r})"

    def __repr__(self):
        primary_attrs = {
            "model_name": self.model_name,
            "action": self.action,
            "entity_name": self.entity_name,
            "read_only": self.read_only,
            "id": self.id,
        }

        primary_str = ", ".join(f"{key}={repr(value)}" for key, value in primary_attrs.items())

        other_attrs = {key: value for key, value in vars(self).items() if not key.startswith("_") and key not in primary_attrs}

        if self.autocomplete_fields:
            other_attrs["autocomplete_fields"] = f"[{len(self.autocomplete_fields)} fields]"
        if self.tabs:
            other_attrs["tabs"] = f"[{len(self.tabs)} tabs]"
        if isinstance(self.entity, dict) and self.entity:
            other_attrs["entity"] = f"[{len(self.entity)} keys]"
        elif self.entity:
            other_attrs["entity"] = f"<{type(self.entity).__name__}>"

        other_str = ", ".join(f"{key}={repr(value)}" for key, value in other_attrs.items())

        full_repr = f"EntityContext({primary_str}"
        if other_str:
            full_repr += f", {other_str}"
        full_repr += ")"

        return full_repr

    def _initialize_derived_fields(self):
        self.model_name = self.entity_table_name or self.__class__.__name__
        self.id = str(getattr(self, "entity_id", ""))
        self.entity_class_name = self.model_name

        blueprint_name = getattr(self, "blueprint_name", "")

        entity_dict = {}
        if self.entity:
            if isinstance(self.entity, dict):
                entity_dict = self.entity
            elif hasattr(self.entity, "__dict__"):
                entity_dict = {k: v for k, v in self.entity.__dict__.items() if not k.startswith("_")}
            elif hasattr(self.entity, "to_dict"):
                entity_dict = self.entity.to_dict()
        elif isinstance(self.entity, dict):
            entity_dict = self.entity

        # Removed: setattr(self, "entity", self.entity) — B010

        if not self.read_only:
            if self.action == "create":
                self.submit_url = url_for(f"{blueprint_name}.create")
            elif self.action == "edit" and self.entity_id:
                self.submit_url = url_for(f"{blueprint_name}.update", entity_id=self.entity_id)
            else:
                self.submit_url = ""
        else:
            self.submit_url = ""

        logger.info(f"📜 Building {self.action!r} page for {blueprint_name!r} blueprint (RO={self.read_only})")
        instance_details = "EntityContext (_initialize_derived_fields)"
        log_instance_vars(instance_details, self)

        self.entity_name = ""
        for key in ("name", "title", "email", "username"):
            if entity_dict.get(key):
                self.entity_name = entity_dict[key]
                logger.info(f"ℹ️ entity_name set using key {key!r}: {self.entity_name!r}")
                break
        else:
            self.entity_name = self.id
            logger.info(f"entity_name defaulted to id: {self.entity_name!r}")
