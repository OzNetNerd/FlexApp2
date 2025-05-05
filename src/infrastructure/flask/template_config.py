"""Template configuration for CRUD operations.

This module provides configuration and utilities for managing template paths
in a standardized way across the application.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TemplateConfig:
    """Configuration for template paths used in CRUD operations.

    Handles template path determination based on model class attributes,
    with fallbacks to sensible defaults.

    Attributes:
        model_class: The model class to derive template information from.
        index_template: Optional custom template path for index views.
        create_template: Optional custom template path for create forms.
        view_template: Optional custom template path for detail views.
        edit_template: Optional custom template path for edit forms.
    """

    model_class: Any
    index_template: Optional[str] = None
    create_template: Optional[str] = None
    view_template: Optional[str] = None
    edit_template: Optional[str] = None

    def __post_init__(self):
        """Set default templates based on model's plural name."""
        if hasattr(self.model_class, "__entity_plural__"):
            plural = self.model_class.__entity_plural__.lower()

            for attr, value in self.__dict__.items():
                if not attr.endswith("_template") or value is not None:
                    continue

                if attr == "index_template":
                    setattr(self, attr, f"pages/{plural}/index.html")
                else:
                    setattr(self, attr, f"pages/{plural}/view.html")

    def get_template(self, route_type: str, default: str) -> str:
        """Get template path with fallback to default.

        Args:
            route_type: Type of route (index, create, view, edit).
            default: Default template path to use if specific isn't set.

        Returns:
            Template path to use for rendering.
        """
        template_attr = f"{route_type}_template"
        if hasattr(self, template_attr):
            template_value = getattr(self, template_attr)
            return template_value or default
        return default
