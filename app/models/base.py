# app/models/base.py

from datetime import date
from collections import OrderedDict

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from app.utils.app_logging import get_logger

logger = get_logger()
db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True

    @declared_attr
    @classmethod
    def __tablename__(cls) -> str:
        """
        Automatically pluralize class names for table names:
        - If the class name ends with 'y', drop the 'y' and add 'ies' (Company → companies)
        - Otherwise just add 's' (User → users)
        """
        name = cls.__name__.lower()
        if name.endswith("y"):
            return name[:-1] + "ies"
        return name + "s"

    @declared_attr
    @classmethod
    def __entity_name__(cls) -> str:
        return cls.__name__

    @declared_attr
    @classmethod
    def __entity_plural__(cls) -> str:
        return cls.__tablename__

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"{self.__class__.__name__} has no attribute {key!r}")
            setattr(self, key, value)

    def to_dict(self) -> dict:
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for rel in self.__mapper__.relationships:
            try:
                val = getattr(self, rel.key)
            except Exception as e:
                logger.warning(f"Error reading relationship {rel.key}: {e}")
                val = None
            if val is None:
                data[rel.key] = None
            elif isinstance(val, list):
                data[rel.key] = [item.id for item in val if hasattr(item, "id")]
            else:
                data[rel.key] = getattr(val, "id", None)
        return data

    def save(self) -> "BaseModel":
        logger.info(f"Saving {self.__class__.__name__}")
        db.session.add(self)
        db.session.commit()
        logger.info(f"Saved {self.__class__.__name__} with ID={self.id}")
        return self

    def delete(self) -> None:
        logger.info(f"Deleting {self.__class__.__name__} ID={self.id}")
        db.session.delete(self)
        db.session.commit()
        logger.info(f"Deleted {self.__class__.__name__} ID={self.id}")

    @staticmethod
    def _infer_widget(col_type) -> str:
        python_type = getattr(col_type, "python_type", None)
        if python_type is int:
            return "number"
        if python_type is bool:
            return "checkbox"
        if python_type is date:
            return "date"
        type_str = str(col_type).lower()
        if "text" in type_str or "clob" in type_str:
            return "textarea"
        return "text"

    @classmethod
    def ui_schema(cls, instance=None) -> dict:
        """
        Generate a UI schema with sections containing form fields.
        Returns a dictionary with section names as keys and lists of fields as values.
        """
        sections = OrderedDict()
        for col in cls.__table__.columns:
            info = col.info or {}
            section_name = info.get("section", "Main")
            if section_name not in sections:
                sections[section_name] = []

            field = {
                "name": col.name,  # Using "name" as expected by the form.html macros
                "entry_name": col.name,  # Keeping entry_name for backward compatibility
                "label": info.get("label", col.name.replace("_", " ").title()),
                "type": info.get("widget", cls._infer_widget(col.type)),
                "value": getattr(instance, col.name) if instance is not None else None,
                "required": info.get("required", not col.nullable),
                "options": info.get("options", []),
                "help_text": info.get("help_text", ""),
            }
            sections[section_name].append(field)

        return sections  # Return dictionary with section names as keys
