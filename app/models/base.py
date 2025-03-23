from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import logging

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy instance to be shared across models
db = SQLAlchemy()

class BaseModel:
    """Base model class for all CRM entities.

    Provides common fields and helper methods for serialization,
    persistence, and deletion of records.

    Attributes:
        id (int): Primary key of the model instance.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
    """

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        """Serialize model instance to dictionary.

        Returns:
            dict: A dictionary of column names and their values.

        Raises:
            AttributeError: If table metadata is missing.
        """
        logger.debug(f"Converting {self.__class__.__name__} instance to dictionary.")
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def save(self):
        """Persist model instance to the database.

        Returns:
            BaseModel: The saved instance for chaining.

        Raises:
            SQLAlchemyError: If commit fails due to DB constraints.
        """
        logger.debug(f"Saving {self.__class__.__name__} instance to the database.")
        db.session.add(self)
        db.session.commit()
        logger.info(f"{self.__class__.__name__} instance saved to the database.")
        return self

    def delete(self) -> None:
        """Remove model instance from the database.

        Raises:
            SQLAlchemyError: If commit fails during deletion.
        """
        logger.debug(f"Deleting {self.__class__.__name__} instance from the database.")
        db.session.delete(self)
        db.session.commit()
        logger.info(f"{self.__class__.__name__} instance deleted from the database.")
