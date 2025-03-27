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
            "fields_by_section": fields,
            "button_text": button_text,
            "item": item,
            "read_only": read_only,
            "edit_url": edit_url,
        }

    def build_fields(self, item=None) -> Dict[str, List[Dict]]:
        """
        Generate ordered, grouped field definitions based on model metadata.

        Args:
            item: SQLAlchemy instance to populate values (optional).

        Returns:
            Dict[str, List[Dict]]: Dictionary grouping fields by section.
        """
        field_definitions = getattr(self.model, "__field_order__", {})
        grouped_fields = defaultdict(list)

        for section, section_fields in field_definitions.items():
            for field in section_fields:
                if isinstance(field, dict):
                    field_copy = field.copy()
                    field_copy["section"] = field_copy.get("section", section)
                    name = field_copy.get("name")
                    field_copy["value"] = self.resolve_value(item, name) if item else ""
                    grouped_fields[field_copy["section"]].append(field_copy)
                else:
                    logger.warning(f"Skipping invalid field (not a dict): {field} in section {section}")

        if current_user.is_authenticated and current_user.is_admin:
            all_users = User.query.order_by(User.name).all()
            selected_user_ids = [str(r.user_id) for r in getattr(item, "relationships", [])]

            grouped_fields["User Access"].append({
                "name": "linked_users",
                "label": "Linked Users",
                "type": "multiselect",
                "options": [{"label": u.name, "value": str(u.id)} for u in all_users],
                "value": selected_user_ids,
                "tab": "Permissions",
                "section": "User Access"
            })

        return dict(grouped_fields)

    def resolve_value(self, item, name: str) -> str:
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
