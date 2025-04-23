from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr

from app.utils.app_logging import get_logger

logger = get_logger()

# Initialize SQLAlchemy instance to be shared across models
db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True

    @declared_attr
    @classmethod
    def __tablename__(cls) -> str:
        """snake_case plural of class name, e.g. Contact → contacts"""
        return cls.__name__.lower() + "s"

    @declared_attr
    @classmethod
    def __entity_name__(cls) -> str:
        """Title-case singular, e.g. 'Contact'"""
        return cls.__name__

    @declared_attr
    @classmethod
    def __entity_plural__(cls) -> str:
        """snake_case plural, same as __tablename__"""
        return cls.__tablename__

    def __init__(self, **kwargs):
        """
        Initialize the model instance using keyword arguments.
        Automatically assigns values to attributes if they exist on the model.
        Raises an error if any provided field does not match an attribute.

        Args:
            **kwargs: Keyword arguments matching model fields.

        Raises:
            AttributeError: If a provided key is not a valid attribute.
        """
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"{self.__class__.__name__} has no attribute {key!r}")
            setattr(self, key, value)

    def to_dict(self) -> dict:
        """
        Serialize the model instance to a dictionary.

        This implementation includes:
         - Column names and their values.
         - Relationship fields (as IDs for many-to-one or one-to-many relationships).

        Returns:
            dict: A dictionary of column names, relationship keys, and their values.
        """
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        for rel in self.__mapper__.relationships:
            try:
                value = getattr(self, rel.key)
            except Exception as e:
                logger.warning(f"Error accessing relationship {rel.key} on {self.__class__.__name__}: {e}")
                value = None

            if value is None:
                data[rel.key] = None
            elif isinstance(value, list):
                data[rel.key] = [entity.id for entity in value if hasattr(entity, "id")]
            else:
                data[rel.key] = value.id if hasattr(value, "id") else None

        return data

    def save(self) -> "BaseModel":
        """
        Persist the model instance to the database.

        Returns:
            BaseModel: The saved instance for chaining.
        """
        logger.info(f"Saving {self.__class__.__name__} instance to the database.")
        db.session.add(self)
        db.session.commit()
        logger.info(f"{self.__class__.__name__} instance saved to the database.")
        return self

    def delete(self) -> None:
        """
        Remove the model instance from the database.
        """
        logger.info(f"Deleting {self.__class__.__name__} instance from the database.")
        db.session.delete(self)
        db.session.commit()
        logger.info(f"{self.__class__.__name__} instance deleted from the database.")
