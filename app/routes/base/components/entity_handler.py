import logging
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, field
from flask import url_for

@dataclass
class TabEntry:
    entry_name: str
    label: str
    type: str
    required: bool = False
    options: Optional[List[dict[str, Any]]] = None
    default: Optional[Any] = None
    value: Optional[Any] = None


@dataclass
class TabSection:
    section_name: str
    entries: List[TabEntry] = field(default_factory=list)

@dataclass
class Tab:
    tab_name: str
    sections: List[TabSection] = field(default_factory=list)

@dataclass
class BasicContext:
    title: str
    item: Optional[Any] = None
    read_only: bool = False


@dataclass
class ResourceContext:
    model: Any
    blueprint_name: str
    item_dict: dict
    item: Optional[str]
    tabs: List[str]
    title: str
    read_only: bool
    error_message: Optional[str] = None
    autocomplete_fields: Optional[List[dict]] = None

    # Derived fields with defaults
    item_name: Optional[str] = None
    submit_url: Optional[str] = None
    id: Optional[str] = None
    ui: Optional[List[str]] = None
    model_name: Optional[str] = None

    def __post_init__(self):
        # Set derived fields
        self.submit_url = url_for(f"{self.blueprint_name}.create") if not self.read_only else ""
        self.model_name = self.model.__name__
        self.id = str(self.item_dict.get("id", ""))
        self.ui = self.tabs

        # Find a display name by checking keys in priority order: name, title, email, username
        # If none are found, fall back to the ID as a string
        name_keys = ["name", "title", "email", "username"]
        for key in name_keys:
            if key in self.item_dict and self.item_dict[key]:
                self.item_name = self.item_dict[key]
                break
        else:
            self.item_name = str(self.item_dict.get("id", ""))

@dataclass
class TableContext:
    page_type: str
    title: str
    table_config: dict
    table_id: str
    data_url: str
    entity_name: str
    add_url: str
    columns: list[Any]

logger = logging.getLogger(__name__)

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