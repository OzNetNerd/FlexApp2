# app/models/base.py

from datetime import date, datetime
from collections import OrderedDict

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from app.utils.app_logging import get_logger

logger = get_logger()
db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    @classmethod
    def __tablename__(cls) -> str:
        """
        Use lowercase class name as table name without pluralization
        """
        return cls.__name__.lower()

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
        # Get column data
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        # Process relationships
        for rel in self.__mapper__.relationships:
            key = rel.key

            # Initialize relationship value to None
            data[key] = None

            try:
                # Try to get the relationship value
                val = getattr(self, key)

                # Only process if not None
                if val is not None:
                    if isinstance(val, list):
                        # Extract IDs from list items
                        data[key] = [item.id for item in val if hasattr(item, "id")]
                    else:
                        # Extract ID from single object
                        data[key] = getattr(val, "id", None)
            except Exception as e:
                # Log error but keep None as the value
                logger.warning(f"Error processing relationship {key}: {e}")

        return data

    def save(self) -> "BaseModel":
        """Persist model instance to the database with logging.

        Returns:
            BaseModel: The saved instance.
        """
        model_name = self.__class__.__name__
        id_str = f"ID={getattr(self, 'id', 'New')}"

        if hasattr(self, "name"):
            id_str += f" {self.name!r}"
        elif hasattr(self, "title"):
            id_str += f" {self.title!r}"

        logger.info(f"Saving {model_name} {id_str}")
        db.session.add(self)
        db.session.commit()
        logger.info(f"Saved {model_name} with ID={self.id}")
        return self

    def delete(self) -> None:
        """Remove model instance from the database with logging."""
        model_name = self.__class__.__name__
        id_str = f"ID={self.id}"

        if hasattr(self, "name"):
            id_str += f" {self.name!r}"
        elif hasattr(self, "title"):
            id_str += f" {self.title!r}"

        logger.info(f"Deleting {model_name} {id_str}")
        db.session.delete(self)
        db.session.commit()
        logger.info(f"Deleted {model_name} {id_str}")

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