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
        logger.info(f"Initializing WebContext with title={title!r}, read_only={read_only}, kwargs={kwargs}")
        super().__init__(**kwargs)

        entity_table_name = kwargs.get("entity_table_name", "")
        logger.info(f"WebContext: entity_table_name from kwargs: {entity_table_name!r}")

        if not title and not entity_table_name:
            logger.error("WebContext initialization failed: Neither 'title' nor 'entity_table_name' provided")
            raise ValueError("Either 'title' or 'entity_table_name' must be provided.")

        self.title = title or kwargs.get("table_name", entity_table_name)
        logger.info(f"WebContext: final title set to: {self.title!r}")
        self.current_user = current_user
        self.entity_table_name = entity_table_name
        logger.info(
            f"WebContext: current_user set to: {current_user.username if hasattr(current_user, 'username') else current_user}")
        self.read_only = read_only
        logger.info(f"WebContext: read_only set to: {read_only}")


class TableContext(WebContext):
    """Context class for rendering table views with table-specific attributes."""

    def __init__(self, entity_table_name=None, title="", read_only=True, action=None, table_data=None, **kwargs):
        logger.info(
            f"Initializing TableContext with entity_table_name={entity_table_name!r}, title={title!r}, action={action!r}")

        # Initialize model_class
        self.model_class = kwargs.pop("model_class", None)
        logger.info(f"TableContext: model_class from kwargs: {self.model_class.__name__ if self.model_class else None}")

        # If model_class is provided but not entity_table_name, derive it
        if self.model_class and not entity_table_name:
            entity_table_name = self.model_class.__entity_name__
            logger.info(f"TableContext: derived entity_table_name from model_class: {entity_table_name!r}")

        if not entity_table_name:
            logger.error("TableContext initialization failed: Neither 'entity_table_name' nor 'model_class' provided")
            raise ValueError("Either 'entity_table_name' or 'model_class' must be provided")

        super().__init__(title=title, read_only=read_only, entity_table_name=entity_table_name, **kwargs)

        self.action = action
        logger.info(f"TableContext: action set to: {action!r}")
        self.table_data = table_data
        logger.info(f"TableContext: table_data set with {len(table_data) if table_data else 0} items")

        # Load model class if not already provided
        if not self.model_class:
            logger.info(f"TableContext: loading model_class for entity: {entity_table_name}")
            from app.utils.model_registry import get_model_by_name

            try:
                self.model_class = get_model_by_name(entity_table_name)
                logger.info(f"TableContext: loaded model_class: {self.model_class.__name__}")
            except ValueError as e:
                logger.error(f"TableContext: Failed to load model class: {e}")
                raise

        # Setup variables needed by templates
        self.page_title = title  # For templates
        self.entity_name = self.model_class.__entity_name__
        logger.info(f"TableContext: entity_name set to: {self.entity_name!r}")
        self.entity_title = title
        logger.info(f"TableContext: entity_title set to: {self.entity_title!r}")
        self.entity_base_route = f"{self.model_class.__tablename__}_bp"
        logger.info(f"TableContext: entity_base_route set to: {self.entity_base_route!r}")
        self.api_url = f"/api/{self.model_class.__tablename__}"
        logger.info(f"TableContext: api_url set to: {self.api_url!r}")
        self.table_id = f"{entity_table_name}_table"
        logger.info(f"TableContext: table_id set to: {self.table_id!r}")
        self.default_sort = "name"
        self.show_heading = kwargs.get("show_heading", True)
        logger.info(f"TableContext: show_heading set to: {self.show_heading}")
        self.show_card_title = kwargs.get("show_card_title", False)
        logger.info(f"TableContext: show_card_title set to: {self.show_card_title}")

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
        logger.info(
            f"Initializing EntityContext with action={action!r}, entity_table_name={entity_table_name!r}, entity_id={entity_id!r}")
        logger.info(f"EntityContext: entity type: {type(entity).__name__}")
        logger.info(
            f"EntityContext: autocomplete_fields: {len(autocomplete_fields) if autocomplete_fields else 0} fields")

        super().__init__(title=title, show_navbar=True, read_only=read_only, entity_table_name=entity_table_name,
                         **kwargs)

        self.autocomplete_fields = autocomplete_fields or []
        self.error_message = error_message
        logger.info(f"EntityContext: error_message set to: {error_message!r}")
        self.title = title or action
        logger.info(f"EntityContext: title set to: {self.title!r}")
        self.entity = entity
        self.action = action
        logger.info(f"EntityContext: action set to: {action!r}")
        self.entity_id = entity_id
        logger.info(f"EntityContext: entity_id set to: {entity_id!r}")

        # Placeholders, may be overwritten by entity_dict
        self.name = "tba"
        self.entity_name = ""
        self.submit_url = ""
        self.model_name = ""
        self.id = ""

        logger.info("EntityContext: About to initialize derived fields")
        self._initialize_derived_fields()
        logger.info("EntityContext: Derived fields initialized")

    def _initialize_derived_fields(self) -> None:
        """Set dynamic fields based on entity data."""
        logger.info("EntityContext._initialize_derived_fields: Beginning derived field initialization")

        self.model_name = self.entity_table_name or self.__class__.__name__
        logger.info(f"EntityContext: model_name set to: {self.model_name!r}")

        self.id = str(getattr(self, "entity_id", ""))
        logger.info(f"EntityContext: id set to: {self.id!r}")

        blueprint_name = request.blueprint or ""
        logger.info(f"EntityContext: blueprint_name from request: {blueprint_name!r}")

        # Build entity dictionary
        logger.info(
            f"EntityContext: Building entity dictionary from entity type: {type(self.entity).__name__ if self.entity else None}")
        entity_dict = {}
        if self.entity:
            if isinstance(self.entity, dict):
                logger.info("EntityContext: entity is already a dictionary")
                entity_dict = self.entity
            elif hasattr(self.entity, "__dict__"):
                logger.info("EntityContext: converting entity.__dict__ to dictionary")
                entity_dict = {k: v for k, v in self.entity.__dict__.items() if not k.startswith("_")}
            elif hasattr(self.entity, "to_dict"):
                logger.info("EntityContext: using entity.to_dict() method")
                entity_dict = self.entity.to_dict()

        logger.info(f"EntityContext: entity_dict created with {len(entity_dict)} keys: {list(entity_dict.keys())}")

        # Set entity attributes
        logger.info("EntityContext: Setting instance attributes from entity_dict")
        for key, value in entity_dict.items():
            setattr(self, key, value)
            logger.info(f"EntityContext: Set self.{key} = {value!r}")

        # Configure submit URL
        logger.info(f"EntityContext: Configuring submit_url with read_only={self.read_only}, action={self.action!r}")
        if not self.read_only:
            if self.action == "create":
                self.submit_url = url_for(f"{blueprint_name}.create")
                logger.info(f"EntityContext: submit_url set to create URL: {self.submit_url!r}")
            elif self.action == "edit" and self.entity_id:
                self.submit_url = url_for(f"{blueprint_name}.update", entity_id=self.entity_id)
                logger.info(f"EntityContext: submit_url set to update URL: {self.submit_url!r}")
            else:
                self.submit_url = ""
                logger.info("EntityContext: submit_url left empty - no matching action/entity_id")
        else:
            self.submit_url = ""
            logger.info("EntityContext: submit_url left empty - read_only mode")

        # Find entity name from common fields
        logger.info("EntityContext: Determining entity_name from common fields")
        for key in ("name", "title", "email", "username"):
            if entity_dict.get(key):
                self.entity_name = entity_dict[key]
                logger.info(f"EntityContext: entity_name set using key {key!r}: {self.entity_name!r}")
                break
        else:
            self.entity_name = self.id
            logger.info(f"EntityContext: entity_name defaulted to id: {self.entity_name!r}")

        # Log variables for debugging
        log_instance_vars("Variables being passed to Jinja", self, exclude=["_sa_instance_state"])