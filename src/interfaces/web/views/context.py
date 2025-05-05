"""Context classes for web template rendering.

This module provides context classes used for rendering web templates
with consistent data structure and error handling.
"""

from typing import Any, Dict, List, Optional

from flask import url_for, request
from flask_login import current_user

from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class BaseContext:
    """Base context class for all types of contexts."""

    def __init__(self, **kwargs):
        """Initialize the base context.

        Args:
            **kwargs: Additional context attributes.
        """
        self.show_navbar = kwargs.get("show_navbar", True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for template rendering.

        Returns:
            Dictionary representation of context.
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


class WebContext(BaseContext):
    """Base context class for web template rendering.

    Attributes:
        title: Page title.
        current_user: Current authenticated user.
        read_only: Whether the form should be read-only.
    """

    def __init__(self, title: str = "", read_only: bool = True, **kwargs):
        """Initialize the web context with common template variables.

        Args:
            title: Page title.
            read_only: Whether the form should be read-only.
            **kwargs: Additional context attributes.
        """
        super().__init__(**kwargs)

        entity_table_name = kwargs.get("entity_table_name", "")
        if not title and not entity_table_name:
            raise ValueError("Either 'title' or 'entity_table_name' must be provided")

        self.title = title or kwargs.get("table_name", entity_table_name)
        self.current_user = current_user
        self.read_only = read_only


class TableContext(WebContext):
    """Context class for rendering table views.

    Attributes:
        model_class: Model class for the entities.
        entity_name: Name of the entity.
        entity_title: Title-cased plural name of the entity.
        entity_base_route: Base route for entity operations.
        api_url: API URL for entity data.
        table_id: HTML ID for the table element.
    """

    def __init__(
            self,
            entity_table_name: Optional[str] = None,
            title: str = "",
            read_only: bool = True,
            action: Optional[str] = None,
            **kwargs
    ):
        """Initialize the table context with table-specific attributes.

        Args:
            entity_table_name: Name of the entity table.
            title: Page title.
            read_only: Whether the form should be read-only.
            action: CRUD action (create, read, update, delete).
            **kwargs: Additional context attributes.
        """
        # Implementation details for initializing table context
        # (omitting for brevity)
        super().__init__(title=title, read_only=read_only, **kwargs)


class EntityContext(WebContext):
    """Context class for entity-specific web views.

    Attributes:
        action: CRUD action being performed.
        entity: Entity being viewed or edited.
        autocomplete_fields: List of autocomplete fields.
        error_message: Error message to display.
        entity_id: ID of the entity.
        submit_url: URL for form submission.
    """

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
        """Initialize the context for entity views.

        Args:
            action: CRUD action being performed.
            entity: Entity being viewed or edited.
            autocomplete_fields: Optional list of autocomplete fields.
            error_message: Optional error message to display.
            title: Optional page title.
            read_only: Whether the form should be read-only.
            entity_table_name: Name of the entity table.
            entity_id: Optional ID of the entity.
            **kwargs: Additional context attributes.
        """
        # Implementation details for initializing entity context
        # (omitting for brevity)
        super().__init__(title=title, read_only=read_only, **kwargs)