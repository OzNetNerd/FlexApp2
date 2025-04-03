import logging
from typing import Any, Dict, List
from dataclasses import dataclass, field
from flask import url_for
from flask_login import current_user
from app.routes.base.tabs import UI_TAB_MAPPING


logger = logging.getLogger(__name__)



@dataclass
class Context:
    """Base context class that allows injecting arbitrary extra fields."""
    title: str = ""
    item: Any = None
    read_only: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for key, value in self.extra.items():
            setattr(self, key, value)


@dataclass
class TableContext:
    page_type: str
    table_config: dict
    table_id: str
    data_url: str
    entity_name: str
    add_url: str
    columns: List[Any]
    title: str = ""
    item: Any = None
    read_only: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        for key, value in self.extra.items():
            setattr(self, key, value)

@dataclass
class ResourceContext:
    model: Any
    blueprint_name: str
    item_dict: dict
    title: str = ""
    autocomplete_fields: list[dict] = field(default_factory=list)
    error_message: str = ""
    item: Any = None
    read_only: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)

    tabs: list = field(default_factory=list, init=False)
    current_user: Any = field(default=None, init=False)
    item_name: str = field(default="", init=False)
    submit_url: str = field(default="", init=False)
    id: str = field(default="", init=False)
    model_name: str = field(default="", init=False)

    def __post_init__(self) -> None:
        for key, value in self.extra.items():
            setattr(self, key, value)

        self.current_user = current_user
        self.submit_url = (
            url_for(f"{self.blueprint_name}.create")
            if not self.read_only else ""
        )
        self.model_name = self.model.__name__
        self.id = str(self.item_dict.get("id", ""))
        self.tabs = UI_TAB_MAPPING[self.model_name](self.item_dict)

        for key in ("name", "title", "email", "username"):
            if self.item_dict.get(key):
                self.item_name = self.item_dict[key]
                break
        else:
            self.item_name = self.id

class EntityHandler:
    """Handles preparation and validation of dynamic form inputs for web routes."""

    def __init__(self, model, service, json_validator):
        """
        Initialize the form handler.

        Args:
            model: SQLAlchemy model class.
            service: Associated CRUD service.
            json_validator: Utility to validate JSON output.
        """
        self.model = model
        self.service = service
        self.json_validator = json_validator

    @staticmethod
    def resolve_value(item, name: str) -> str:
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
    def validate_create(form_data: Dict) -> List[str]:
        """
        Validate form data before creating a record.

        Args:
            form_data (Dict): Form input.

        Returns:
            List[str]: List of validation errors.
        """
        users = form_data.getlist("users")
        companies = form_data.getlist("companies")

        logger.info(f"👥 Selected user IDs: {users}")
        logger.info(f"🏢 Selected company IDs: {companies}")

        return []

    @staticmethod
    def validate_edit(item, form_data: Dict) -> List[str]:
        """
        Validate form data before updating a record.

        Args:
            item: SQLAlchemy instance being edited.
            form_data (Dict): Updated form input.

        Returns:
            List[str]: List of validation errors.
        """
        users = form_data.getlist("users")
        companies = form_data.getlist("companies")

        logger.info(f"✏️ [Edit] Selected user IDs: {users}")
        logger.info(f"✏️ [Edit] Selected company IDs: {companies}")

        return []