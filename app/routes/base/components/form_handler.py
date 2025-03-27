import logging
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

    def prepare_form_context(
        self,
        title: str,
        submit_url: str,
        cancel_url: str,
        fields: List[Dict],
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
            "fields": fields,
            "button_text": button_text,
            "item": item,
            "read_only": read_only,
            "edit_url": edit_url,
        }

    def build_fields(self, item=None) -> List[Dict]:
        """
        Generate dynamic field definitions based on model metadata.

        Args:
            item: SQLAlchemy instance to populate values (optional).

        Returns:
            List[Dict]: List of field definitions.
        """
        field_definitions = getattr(self.model, "__field_order__", [])
        fields = []

        for field in field_definitions:
            # Ensure field is a dictionary before copying
            if isinstance(field, dict):
                field_copy = field.copy()
                name = field_copy.get("name")
                field_copy["value"] = self.resolve_value(item, name) if item else ""
                fields.append(field_copy)
            else:
                logger.warning(f"Skipping field because it's not a dictionary: {field}")

        if current_user.is_authenticated and current_user.is_admin:
            all_users = User.query.order_by(User.name).all()
            selected_user_ids = [str(r.user_id) for r in getattr(item, "relationships", [])]

            fields.append(
                {
                    "name": "linked_users",
                    "label": "Linked Users",
                    "type": "multiselect",
                    "options": [{"label": u.name, "value": str(u.id)} for u in all_users],
                    "value": selected_user_ids,
                }
            )

        return fields

    def resolve_value(self, item, name: str) -> str:
        """
        Resolve nested attribute values from an object using dot notation.

        Args:
            item: Object to resolve from.
            name (str): Dot notation string (e.g. "company.name").

        Returns:
            str: Resolved value or empty string.
        """
        try:
            for part in name.split("."):
                item = getattr(item, part)
            return item
        except AttributeError:
            logger.warning(f"Unable to resolve value for '{name}'")
            return ""

    def validate_create(self, form_data: Dict) -> List[str]:
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

    def validate_edit(self, item, form_data: Dict) -> List[str]:
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
