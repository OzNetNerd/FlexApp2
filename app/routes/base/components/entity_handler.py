import logging
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, field
from flask import url_for
from flask_login import current_user
from app.routes.base.tabs import UI_TAB_MAPPING


logger = logging.getLogger(__name__)


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
    title: str
    read_only: bool

    tabs: List = field(init=False)
    current_user: Any = field(init=False)
    item: Optional[str] = None
    error_message: Optional[str] = None
    autocomplete_fields: List[dict] = field(default_factory=list)  # Use default_factory=list instead of None

    # Derived fields with defaults
    item_name: Optional[str] = None
    submit_url: Optional[str] = None
    id: Optional[str] = None
    model_name: Optional[str] = None

    def __post_init__(self):
        # Set derived fields
        self.current_user = current_user
        self.submit_url = url_for(f"{self.blueprint_name}.create") if not self.read_only else ""
        self.model_name = self.model.__name__
        self.id = str(self.item_dict.get("id", ""))
        self.tabs = UI_TAB_MAPPING[self.model.__name__](self.item_dict)

        # logger.error("UI TABS")
        # logger.error(UI_TAB_MAPPING)
        # logger.error(f'Name: {self.model.__name__}')
        # logger.error(f'Item: {self.item_dict}')
        # logger.error(f'Result: {result}')

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