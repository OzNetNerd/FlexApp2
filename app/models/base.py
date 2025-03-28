from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import logging


logger = logging.getLogger(__name__)

# Initialize SQLAlchemy instance to be shared across models
db = SQLAlchemy()

class BaseModel(db.Model):
    """Base model class for all CRM entities.

    Provides common fields and helper methods for serialization,
    persistence, and deletion of records.

    Attributes:
        id (int): Primary key of the model instance.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
    """

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
                raise AttributeError(f"{self.__class__.__name__} has no attribute '{key}'")
            setattr(self, key, value)

    def to_dict(self) -> dict:
        """
        Serialize the model instance to a dictionary.

        Returns:
            dict: A dictionary of column names and their values.
        """
        logger.debug(f"Converting {self.__class__.__name__} instance to dictionary.")
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def save(self) -> "BaseModel":
        """
        Persist the model instance to the database.

        Returns:
            BaseModel: The saved instance for chaining.
        """
        logger.debug(f"Saving {self.__class__.__name__} instance to the database.")
        db.session.add(self)
        db.session.commit()
        logger.info(f"{self.__class__.__name__} instance saved to the database.")
        return self

    def delete(self) -> None:
        """
        Remove the model instance from the database.
        """
        logger.debug(f"Deleting {self.__class__.__name__} instance from the database.")
        db.session.delete(self)
        db.session.commit()
        logger.info(f"{self.__class__.__name__} instance deleted from the database.")
