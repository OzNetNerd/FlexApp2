"""
Base SQLAlchemy model and database configuration.

This module provides the database connection and base model class that
all SQLAlchemy models inherit from.
"""
from collections import OrderedDict
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declared_attr

from infrastructure.logging import get_logger

logger = get_logger(__name__)

# SQLAlchemy instance
db = SQLAlchemy()

T = TypeVar('T', bound='BaseModel')


class BaseModel(db.Model):
    """
    Base SQLAlchemy model providing common functionality.

    All database models should inherit from this class to gain common
    functionality like timestamps, serialization, and CRUD operations.

    Attributes:
        id: Primary key for the model.
        created_at: When the record was created.
        updated_at: When the record was last updated.
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    @classmethod
    def __tablename__(cls) -> str:
        """
        Automatically pluralize class names for table names.

        Returns:
            The table name derived from the model class name.
        """
        name = cls.__name__.lower()
        if name.endswith("y"):
            return name[:-1] + "ies"
        return name + "s"

    @declared_attr
    @classmethod
    def __entity_name__(cls) -> str:
        """
        Gets the singular entity name.

        Returns:
            The entity name (class name).
        """
        return cls.__name__

    @declared_attr
    @classmethod
    def __entity_plural__(cls) -> str:
        """
        Gets the plural entity name.

        Returns:
            The plural entity name (table name).
        """
        return cls.__tablename__

    def __init__(self, **kwargs) -> None:
        """
        Initialize a model instance with the provided attributes.

        Args:
            **kwargs: Attribute values to set on the instance.

        Raises:
            AttributeError: If an unknown attribute is provided.
        """
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"{self.__class__.__name__} has no attribute {key!r}")
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model instance to a dictionary.

        Returns:
            Dictionary representation of the model.
        """
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
        """
        Persist model instance to the database with logging.

        Returns:
            The saved instance.
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

    @classmethod
    def find_by_id(cls: Type[T], id: int) -> Optional[T]:
        """
        Find a model instance by its primary key.

        Args:
            id: The primary key value to look for.

        Returns:
            The model instance if found, None otherwise.
        """
        return cls.query.get(id)

    @classmethod
    def find_all(cls: Type[T]) -> List[T]:
        """
        Find all instances of this model.

        Returns:
            List of all instances.
        """
        return cls.query.all()

    @staticmethod
    def _infer_widget(col_type) -> str:
        """
        Infer the appropriate UI widget type for a column.

        Args:
            col_type: The SQLAlchemy column type.

        Returns:
            String name of the appropriate widget type.
        """
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
    def ui_schema(cls, instance=None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate a UI schema with sections containing form fields.

        Args:
            instance: Optional model instance to extract values from.

        Returns:
            Dictionary with section names as keys and lists of fields as values.
        """
        sections = OrderedDict()
        for col in cls.__table__.columns:
            info = col.info or {}
            section_name = info.get("section", "Main")
            if section_name not in sections:
                sections[section_name] = []

            field = {
                "name": col.name,
                "entry_name": col.name,
                "label": info.get("label", col.name.replace("_", " ").title()),
                "type": info.get("widget", cls._infer_widget(col.type)),
                "value": getattr(instance, col.name) if instance is not None else None,
                "required": info.get("required", not col.nullable),
                "options": info.get("options", []),
                "help_text": info.get("help_text", ""),
            }
            sections[section_name].append(field)

        return sections