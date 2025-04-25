# models/form_metadata.py
from app.models.base import BaseModel, db
from app.utils.app_logging import get_logger
from sqlalchemy.ext.declarative import declared_attr
from typing import List, Dict, Any, Optional
import json

logger = get_logger()


class FormTab(BaseModel):
    __tablename__ = "form_tabs"

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False)  # 'Company', 'Contact', etc.
    name = db.Column(db.String(50), nullable=False)  # Tab name displayed to user
    order = db.Column(db.Integer, nullable=False)
    visible_on_create = db.Column(db.Boolean, default=True)
    visible_on_edit = db.Column(db.Boolean, default=True)
    visible_on_view = db.Column(db.Boolean, default=True)

    sections = db.relationship("FormSection", back_populates="tab",
                               cascade="all, delete-orphan", order_by="FormSection.order")

    __table_args__ = (db.UniqueConstraint('entity_type', 'name'),)

    @classmethod
    def get_tabs_for_entity(cls, entity_type: str, mode: str = "view") -> List["FormTab"]:
        """Get all tabs for an entity type in the specified mode (create, edit, view)"""
        query = cls.query.filter_by(entity_type=entity_type)

        if mode == "create":
            query = query.filter_by(visible_on_create=True)
        elif mode == "edit":
            query = query.filter_by(visible_on_edit=True)
        elif mode == "view":
            query = query.filter_by(visible_on_view=True)

        return query.order_by(cls.order).all()


class FormSection(BaseModel):
    __tablename__ = "form_sections"

    id = db.Column(db.Integer, primary_key=True)
    tab_id = db.Column(db.Integer, db.ForeignKey("form_tabs.id"), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    order = db.Column(db.Integer, nullable=False)

    tab = db.relationship("FormTab", back_populates="sections")
    fields = db.relationship("FormField", back_populates="section",
                             cascade="all, delete-orphan", order_by="FormField.order")

    __table_args__ = (db.UniqueConstraint('tab_id', 'name'),)


class FormField(BaseModel):
    __tablename__ = "form_fields"

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey("form_sections.id"), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)  # Database column name
    label = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)  # 'text', 'textarea', etc.
    required = db.Column(db.Boolean, default=False)
    visible_on_create = db.Column(db.Boolean, default=True)
    visible_on_edit = db.Column(db.Boolean, default=True)
    visible_on_view = db.Column(db.Boolean, default=True)
    readonly_on_create = db.Column(db.Boolean, default=False)
    readonly_on_edit = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, nullable=False)
    options_json = db.Column(db.Text, nullable=True)  # For select/radio/checkbox fields

    section = db.relationship("FormSection", back_populates="fields")

    __table_args__ = (db.UniqueConstraint('section_id', 'field_name'),)

    @property
    def options(self) -> List[Dict[str, Any]]:
        """Parse options from JSON string"""
        if not self.options_json:
            return []
        try:
            return json.loads(self.options_json)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in options_json for field {self.id}")
            return []

    @options.setter
    def options(self, value: List[Dict[str, Any]]) -> None:
        """Set options as JSON string"""
        self.options_json = json.dumps(value)

    @property
    def entity_type(self) -> str:
        """Get entity type from parent tab"""
        return self.section.tab.entity_type if self.section and self.section.tab else None


class FormDefinition:
    """Helper class for working with form definitions"""

    @staticmethod
    def get_form_definition(entity_type: str, mode: str = "view") -> Dict[str, Any]:
        """Get complete form definition for an entity type

        Args:
            entity_type: The type of entity (e.g., 'Company', 'Contact')
            mode: The form mode ('create', 'edit', or 'view')

        Returns:
            Dict with complete form definition including tabs, sections, and fields
        """
        tabs = FormTab.get_tabs_for_entity(entity_type, mode)

        form_def = {
            "entity_type": entity_type,
            "mode": mode,
            "tabs": []
        }

        for tab in tabs:
            tab_def = {
                "id": tab.id,
                "name": tab.name,
                "sections": []
            }

            for section in tab.sections:
                section_def = {
                    "id": section.id,
                    "name": section.name,
                    "fields": []
                }

                fields_query = FormField.query.filter_by(section_id=section.id)

                if mode == "create":
                    fields_query = fields_query.filter_by(visible_on_create=True)
                elif mode == "edit":
                    fields_query = fields_query.filter_by(visible_on_edit=True)
                elif mode == "view":
                    fields_query = fields_query.filter_by(visible_on_view=True)

                fields = fields_query.order_by(FormField.order).all()

                for field in fields:
                    readonly = False
                    if mode == "create" and field.readonly_on_create:
                        readonly = True
                    elif mode == "edit" and field.readonly_on_edit:
                        readonly = True
                    elif mode == "view":
                        readonly = True

                    field_def = {
                        "id": field.id,
                        "field_name": field.field_name,
                        "label": field.label,
                        "field_type": field.field_type,
                        "required": field.required,
                        "readonly": readonly,
                        "options": field.options
                    }

                    section_def["fields"].append(field_def)

                if section_def["fields"]:  # Only include sections with fields
                    tab_def["sections"].append(section_def)

            if tab_def["sections"]:  # Only include tabs with sections
                form_def["tabs"].append(tab_def)

        return form_def