import logging
from typing import Dict, List, Any, Optional

from dataclasses import dataclass, field

@dataclass
class IndexContext:
    page_type: str
    title: str
    table_config: dict
    table_id: str
    data_url: str
    entity_name: str
    add_url: str
    columns: list[Any]


@dataclass
class ResourceContext:
    title: str = ""
    model_name: str = ""
    item_name: str = ""
    submit_url: str = ""
    cancel_url: str = ""
    tabs: dict = field(default_factory=dict)
    id: str = ""
    item: Any = ""
    read_only: bool = True
    error_message: str = None


@dataclass
class TabEntry:
    entry_name: str
    label: str
    type: str
    required: bool = False
    readonly: bool = True
    options: Optional[List[dict[str, Any]]] = None
    default: Optional[Any] = None

@dataclass
class TabSection:
    section_name: str
    entries: List[TabEntry] = field(default_factory=list)

@dataclass
class Tab:
    tab_name: str
    sections: List[TabSection] = field(default_factory=list)


logger = logging.getLogger(__name__)

class FormHandler:
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