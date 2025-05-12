from typing import Any, List, Optional

from flask import url_for, request
from flask_login import current_user

from app.routes.base_context import BaseContext
from app.utils.app_logging import get_logger, log_instance_vars

logger = get_logger()


class WebContext(BaseContext):
    """Base context class for web template rendering."""

    def __init__(self, title="", read_only=True, **kwargs):
        """Initialize the web context with common template variables."""
        super().__init__(**kwargs)

        entity_table_name = kwargs.get("entity_table_name", "")
        if not title and not entity_table_name:
            raise ValueError("Either 'title' or 'entity_table_name' must be provided.")

        self.title = title or kwargs.get("table_name", entity_table_name)
        self.current_user = current_user
        self.read_only = read_only


class TableContext(WebContext):
    """Context class for rendering table views with table-specific attributes."""

    def __init__(self, entity_table_name=None, title="", read_only=True, action=None, **kwargs):
        # Initialize model_class
        self.model_class = kwargs.pop("model_class", None)

        # If model_class is provided but not entity_table_name, derive it
        if self.model_class and not entity_table_name:
            entity_table_name = self.model_class.__entity_name__

        if not entity_table_name:
            raise ValueError("Either 'entity_table_name' or 'model_class' must be provided")

        self.action = action

        # Load model class if not already provided
        if not self.model_class:
            from app.utils.model_registry import get_model_by_name

            self.model_class = get_model_by_name(entity_table_name)


        title = title or entity_table_name

        # Determine plural name
        # entity_plural = self.model_class.__entity_plural__

        # Set page title
        # if title:
        #     page_title = title
        # else:
        #     page_title = f"{action.capitalize()} {entity_table_name}"
            # page_title = f"{action.capitalize()} {entity_table_name}" if action else entity_plural.capitalize()

        # Call parent with processed values
        super().__init__(title=title, show_navbar=True, read_only=read_only, entity_table_name=entity_table_name, **kwargs)

        # Setup variables needed by templates
        self.page_title = title  # For templates
        self.entity_name = self.model_class.__entity_name__
        self.entity_title = title
        self.entity_base_route = f"{self.model_class.__tablename__}_bp"
        self.api_url = f"/api/{self.model_class.__tablename__}"
        self.table_id = f"{entity_table_name}_table"
        self.default_sort = "name"
        self.show_heading = kwargs.get("show_heading", True)
        self.show_card_title = kwargs.get("show_card_title", False)

        logger.info(f"TableContext initialized for {self.entity_name} ({self.entity_base_route})")


class EntityContext(WebContext):
    """Context class for entity-specific web views."""

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
        """Initialize the context for entity views."""
        super().__init__(title=title, show_navbar=True, read_only=read_only, entity_table_name=entity_table_name, **kwargs)

        self.autocomplete_fields = autocomplete_fields or []
        self.error_message = error_message
        self.title = title or action
        self.entity = entity
        self.action = action
        self.entity_id = entity_id

        # Placeholders, may be overwritten by entity_dict
        self.name = "tba"
        self.entity_name = ""
        self.submit_url = ""
        self.model_name = ""
        self.id = ""

        self._initialize_derived_fields()

    def _initialize_derived_fields(self) -> None:
        """Set dynamic fields based on entity data."""
        self.model_name = self.entity_table_name or self.__class__.__name__
        self.id = str(getattr(self, "entity_id", ""))
        blueprint_name = request.blueprint or ""

        # Build entity dictionary
        entity_dict = {}
        if self.entity:
            if isinstance(self.entity, dict):
                entity_dict = self.entity
            elif hasattr(self.entity, "__dict__"):
                entity_dict = {k: v for k, v in self.entity.__dict__.items() if not k.startswith("_")}
            elif hasattr(self.entity, "to_dict"):
                entity_dict = self.entity.to_dict()

        # Set entity attributes
        for key, value in entity_dict.items():
            setattr(self, key, value)

        # Configure submit URL
        if not self.read_only:
            if self.action == "create":
                self.submit_url = url_for(f"{blueprint_name}.create")
            elif self.action == "edit" and self.entity_id:
                self.submit_url = url_for(f"{blueprint_name}.update", entity_id=self.entity_id)
            else:
                self.submit_url = ""
        else:
            self.submit_url = ""

        # Find entity name from common fields
        for key in ("name", "title", "email", "username"):
            if entity_dict.get(key):
                self.entity_name = entity_dict[key]
                logger.info(f"ℹ️ entity_name set using key {key!r}: {self.entity_name!r}")
                break
        else:
            self.entity_name = self.id
            logger.info(f"ℹ️ entity_name defaulted to id: {self.entity_name!r}")

        # Log variables for debugging
        log_instance_vars("Variables being passed to Jinja", self, exclude=["_sa_instance_state"])
