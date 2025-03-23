from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import logging

logger = logging.getLogger(__name__)

db = SQLAlchemy()


class BaseModel:
    """Base model class that includes common columns and methods."""

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        """Convert model to dictionary."""
        logger.debug(f"Converting {self.__class__.__name__} instance to dictionary.")
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def save(self):
        """Save instance to database."""
        logger.debug(f"Saving {self.__class__.__name__} instance to the database.")
        db.session.add(self)
        db.session.commit()
        logger.info(f"{self.__class__.__name__} instance saved to the database.")
        return self

    def delete(self):
        """Delete instance from database."""
        logger.debug(f"Deleting {self.__class__.__name__} instance from the database.")
        db.session.delete(self)
        db.session.commit()
        logger.info(f"{self.__class__.__name__} instance deleted from the database.")
