# MIGRATED

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class TemplateConfig:
    """Shared configuration for template paths used in CRUD operations."""

    model_class: Any
    index_template: Optional[str] = None
    create_template: Optional[str] = None
    view_template: Optional[str] = None
    edit_template: Optional[str] = None

    def __post_init__(self):
        # Set default templates based on model's plural name
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
        """Get template path with fallback to default."""
        template_attr = f"{route_type}_template"
        if hasattr(self, template_attr):
            template_value = getattr(self, template_attr)
            return template_value or default
        return default
