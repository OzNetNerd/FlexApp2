import logging
from collections import defaultdict
from typing import Dict, List
from flask_login import current_user
from app.models import User


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
    def prepare_form_context(
            title: str,
            submit_url: str,
            cancel_url: str,
            fields: Dict[str, List[Dict]],  # Dictionary with section names as keys
            button_text: str = None,
            item=None,
            read_only: bool = False,
            edit_url: str = None,
    ) -> Dict:
        """
        Generate a context dictionary for form templates.
        Returns:
            Dict: Render context.
        """
        return {
            "title": title,
            "submit_url": submit_url,
            "cancel_url": cancel_url,
            "fields": fields,  # Keep your original structure
            "button_text": button_text,
            "item": item,
            "read_only": read_only,
            "edit_url": edit_url,
        }

    def _validate_and_log_field_order(self) -> Dict[str, List[Dict]]:
        """
        Validate and log the structure of the model's __field_order__ metadata.

        Logs the number of sections and fields defined in the model's `__field_order__`.
        If `__field_order__` is missing, a ValueError is raised.

        Returns:
            Dict[str, List[Dict]]: The validated __field_order__ dictionary.

        Raises:
            ValueError: If __field_order__ is not defined on the model.
        """
        field_definitions = getattr(self.model, "__field_order__", {})
        if not field_definitions:
            logger.error(f"__field_order__ not found for model {self.model.__name__}")
            raise ValueError(f"__field_order__ is required for model {self.model.__name__}")

        logger.info(
            f"Found {len(field_definitions)} sections in __field_order__ for model {self.model.__name__}: {', '.join(field_definitions.keys())}"
        )

        for section, fields in field_definitions.items():
            names = [f["name"] for f in fields if isinstance(f, dict) and "name" in f]
            logger.info(f"  Section '{section}' has {len(names)} field(s): {', '.join(names)}")
        return field_definitions

    def build_fields(self, item=None) -> Dict[str, List[Dict]]:
        """
        Generate ordered, grouped field definitions based on model metadata,
        injecting values from a given SQLAlchemy instance.

        This method processes the model's `__field_order__` metadata to produce
        a dictionary of fields grouped by section. If an item is provided,
        each field will include a resolved `value` based on that instance.

        If the current user is an admin, additional admin-only fields defined in
        `__admin_fields__` will be injected and also populated.

        Args:
            item (Optional[Base]): SQLAlchemy model instance to extract field values from.

        Returns:
            Dict[str, List[Dict]]: A dictionary where each key is a section name and
            the value is a list of field definitions (with metadata and resolved values).
        """
        grouped_fields = defaultdict(list)
        field_definitions = self._validate_and_log_field_order()
        required_keys = {"name", "type", "label"}

        for section, section_fields in field_definitions.items():
            for field in section_fields:
                if not isinstance(field, dict):
                    logger.warning(f"Skipping invalid field (not a dict): {field} in section {section}")
                    continue
                missing = required_keys - field.keys()
                if missing:
                    raise ValueError(
                        f"Field in section '{section}' is missing required keys: {', '.join(missing)} — field: {field}")
                field_copy = field.copy()
                field_copy["section"] = field_copy.get("section", section)
                name = field_copy.get("name")
                field_copy["value"] = self.resolve_value(item, name) if item else ""
                grouped_fields[field_copy["section"]].append(field_copy)

        if current_user.is_authenticated and current_user.is_admin:
            for field in getattr(self.model, "__admin_fields__", []):
                if not isinstance(field, dict):
                    logger.warning(f"Skipping invalid admin field (not a dict): {field}")
                    continue
                missing = required_keys - field.keys()
                if missing:
                    raise ValueError(f"Admin field is missing required keys: {', '.join(missing)} — field: {field}")
                if field.get("name") == "linked_users":
                    field["value"] = [str(r.user_id) for r in getattr(item, "relationships", [])]
                    field["options"] = [
                        {"label": u.name, "value": str(u.id)}
                        for u in User.query.order_by(User.name).all()
                    ]
                field_copy = field.copy()
                field_copy["section"] = field_copy.get("section", "Admin")
                name = field_copy.get("name")
                field_copy["value"] = self.resolve_value(item, name) if item else ""
                grouped_fields[field_copy["section"]].append(field_copy)

        logger.debug(f"Returning grouped_fields:\n{grouped_fields}")
        return dict(grouped_fields)

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
