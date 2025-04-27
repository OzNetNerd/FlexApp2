# routes/web/context.py

from typing import Any, List, Optional

from flask import url_for, request
from flask_login import current_user

from app.utils.app_logging import get_logger, log_instance_vars
from app.utils.table_helpers import get_table_id_by_name

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
        # log_instance_vars(instance_details, self)

        if not title and not kwargs.get("entity_table_name"):
            raise ValueError("Either 'title' or 'entity_table_name' must be provided.")

        self.title = title or kwargs["table_name"]
        self.current_user = current_user
        self.show_navbar = show_navbar
        self.read_only = read_only

        # Set each keyword argument as an attribute on the instance.
        logger.info(f"Setting kwargs as instance variables:")
        for key, value in kwargs.items():
            setattr(self, key, value)
            logger.info(f"  📝 Set attribute {key!r} = {value!r}")

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

    def __init__(self, entity_table_name=None, title="", read_only=True, action=None, **kwargs):
        # Allow either entity_table_name or model_class as input
        self.model_class = kwargs.pop('model_class', None)

        # If model_class is provided but not entity_table_name, derive it
        if self.model_class and not entity_table_name:
            entity_table_name = self.model_class.__entity_name__

        if not entity_table_name:
            raise ValueError("Either 'entity_table_name' or 'model_class' must be provided")

        self.entity_table_name = entity_table_name
        self.read_only = read_only
        self.action = action

        # Load model class if not already provided
        if not self.model_class:
            from app.utils.model_registry import get_model_by_name
            self.model_class = get_model_by_name(entity_table_name)

        # Determine plural name (with fallback)
        entity_plural = getattr(self.model_class, '__entity_plural__', self.entity_table_name.lower() + 's')

        # Set page title and display title
        if title:
            self.title = title
        else:
            self.title = f"{action.capitalize()} {entity_table_name}" if action else entity_plural.capitalize()

        self.page_title = self.title  # ✅ Explicitly set page_title for templates

        super().__init__(title=self.title, **kwargs)


        # Variables needed by _table_index.html
        self.entity_name = self.model_class.__entity_name__
        self.entity_title = getattr(self.model_class, '__entity_plural__', '').capitalize() or f"{self.entity_name}s"
        self.entity_base_route = f"{self.model_class.__tablename__}_bp"
        self.api_url = f"/api/{self.model_class.__tablename__}"
        self.table_id = get_table_id_by_name(self.entity_table_name)
        self.default_sort = "name"
        self.show_heading = kwargs.get('show_heading', True)
        self.show_card_title = kwargs.get('show_card_title', False)

        logger.info(f"TableContext initialized for {self.entity_name} ({self.entity_base_route})")

    def __str__(self):
        """Return a user-friendly string representation focusing on table attributes."""
        return f"TableContext(entity_table_name={self.entity_table_name!r}, entity_title={self.entity_title!r})"


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
    ) -> None:
        """Initialize the context and derive dynamic fields."""
        super().__init__(
            title=title,
            show_navbar=True,
            read_only=read_only,
            entity_table_name=entity_table_name,
            table_name=entity_table_name,
            **kwargs,
        )
        self.autocomplete_fields: List[dict] = autocomplete_fields or []
        self.error_message: str = error_message
        self.title: str = title or action
        self.entity: Any = entity
        self.read_only: bool = read_only
        self.action: str = action
        self.current_user = current_user
        self.entity_table_name: str = entity_table_name
        self.entity_id: Any = entity_id
        # placeholders, may be overwritten by entity_dict
        self.name: str = "tba"
        self.entity_name: str = ""
        self.submit_url: str = ""
        self.model_name: str = ""
        self.id: str = ""

        self._initialize_derived_fields()

    def __str__(self) -> str:
        return f"EntityContext(model={self.model_name!r}, action={self.action!r}, entity={self.entity_name!r})"

    def __repr__(self) -> str:
        primary_attrs = {
            "model_name": self.model_name,
            "action": self.action,
            "entity_name": self.entity_name,
            "read_only": self.read_only,
            "id": self.id,
        }
        primary_str = ", ".join(f"{key}={value!r}" for key, value in primary_attrs.items())
        other_attrs: Dict[str, Any] = {
            key: value
            for key, value in vars(self).items()
            if not key.startswith("_") and key not in primary_attrs
        }
        if self.autocomplete_fields:
            other_attrs["autocomplete_fields"] = f"[{len(self.autocomplete_fields)} fields]"

        other_str = ", ".join(f"{key}={value!r}" for key, value in other_attrs.items())
        full_repr = f"EntityContext({primary_str}"
        if other_str:
            full_repr += f", {other_str}"
        full_repr += ")"
        return full_repr

    def _initialize_derived_fields(self) -> None:
        """Derive dynamic fields, assign entity attributes, and log state."""
        self.model_name = self.entity_table_name or self.__class__.__name__
        self.id = str(getattr(self, "entity_id", ""))
        blueprint_name = request.blueprint or ""

        # Build a dict of entity attributes
        entity_dict: Dict[str, Any] = {}
        if self.entity:
            if isinstance(self.entity, dict):
                entity_dict = self.entity
            elif hasattr(self.entity, "__dict__"):
                entity_dict = {
                    k: v for k, v in self.entity.__dict__.items() if not k.startswith("_")
                }
            elif hasattr(self.entity, "to_dict"):
                entity_dict = self.entity.to_dict()

        # Assign all entity fields onto this context object
        for key, value in entity_dict.items():
            setattr(self, key, value)

        # Configure submit URL based on action
        if not self.read_only:
            if self.action == "create":
                self.submit_url = url_for(f"{blueprint_name}.create")
            elif self.action == "edit" and self.entity_id:
                self.submit_url = url_for(
                    f"{blueprint_name}.update", entity_id=self.entity_id
                )
            else:
                self.submit_url = ""
        else:
            self.submit_url = ""

        # Log context state
        logger.info(
            f"📜 Building {self.action!r} page for {blueprint_name!r} blueprint (RO={self.read_only})"
        )
        # log_instance_vars("EntityContext (_initialize_derived_fields)", self)

        # Log all model instance variables, excluding SQLAlchemy internals
        log_instance_vars(
            "Entity model variables", self.entity, exclude=["_sa_instance_state"]
        )

        # Determine a friendly name for the entity
        for key in ("name", "title", "email", "username"):
            if entity_dict.get(key):
                self.entity_name = entity_dict[key]
                logger.info(
                    f"ℹ️ entity_name set using key {key!r}: {self.entity_name!r}"
                )
                break
        else:
            self.entity_name = self.id
            logger.info(
                f"ℹ️ entity_name defaulted to id: {self.entity_name!r}"
            )
