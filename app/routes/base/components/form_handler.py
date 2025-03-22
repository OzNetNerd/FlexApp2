import logging
from typing import Dict, List
from flask import url_for

logger = logging.getLogger(__name__)


class FormHandler:
    """Handles form preparation and validation."""

    def __init__(self, model, service, json_validator):
        self.model = model
        self.service = service
        self.json_validator = json_validator

    def prepare_form_context(self, title, submit_url, cancel_url, fields, button_text=None, item=None, read_only=False,
                             edit_url=None):
        """
        Builds the context dictionary for rendering form templates.
        """
        context = {
            'title': title,
            'submit_url': submit_url,
            'cancel_url': cancel_url,
            'fields': fields,
            'button_text': button_text,
            'item': item,
            'read_only': read_only,
            'edit_url': edit_url
        }
        return context

    def build_fields(self, item=None) -> List[Dict]:
        """
        Builds form fields dynamically based on the model's __field_order__.

        Returns:
            List[Dict]: A list of dictionaries defining the form fields.
        """
        field_definitions = getattr(self.model, '__field_order__', [])
        fields = []

        for field in field_definitions:
            field_copy = field.copy()
            name = field_copy.get("name")

            # Populate value if item is provided
            field_copy["value"] = self.resolve_value(item, name) if item else ""
            fields.append(field_copy)

        return fields

    def resolve_value(self, item, name: str):
        """
        Resolves dot-notation attribute access on the item object.
        Example: 'company.name' -> item.company.name
        """
        try:
            for part in name.split('.'):
                item = getattr(item, part)
            return item
        except AttributeError:
            logger.warning(f"Unable to resolve value for '{name}'")
            return ""

    def validate_create(self, form_data: Dict) -> List[str]:
        """Validate form data for create operation."""
        return []

    def validate_edit(self, item, form_data: Dict) -> List[str]:
        """Validate form data for edit operation."""
        return []
