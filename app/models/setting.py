from sqlalchemy import inspect

from app.models.base import BaseModel, db
from app.utils.app_logging import get_logger

logger = get_logger()


class Setting(BaseModel):
    """Represents application-level settings configured by code, editable via UI."""

    __tablename__ = "settings"

    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    SETTINGS = {
        "debug_mode": "false",
        "maintenance_mode": "false",
        "feature_x_enabled": "true",
    }

    def __repr__(self) -> str:
        return f"<Setting {self.key}: {self.value}>"

    def save(self) -> "Setting":
        logger.info(f"Saving setting '{self.key}' with value '{self.value}'")
        super().save()
        logger.info(f"Setting '{self.key}' saved successfully.")
        return self

    def delete(self) -> None:
        logger.info(f"Deleting setting '{self.key}'")
        super().delete()
        logger.info(f"Setting '{self.key}' deleted successfully.")

    @classmethod
    def seed(cls) -> None:
        """Ensure all app settings exist in the DB with defaults if needed."""
        inspector = inspect(db.engine)
        logger.info("🔧 Checking for existence of 'settings' table")

        if cls.__tablename__ not in inspector.get_table_names():
            logger.warning(f"⚠️ Table '{cls.__tablename__}' does not exist. Creating")
            db.create_all()
            logger.info(f"Table '{cls.__tablename__}' created successfully.")

        logger.info("🔍 Verifying required settings in the database")

        for key, default_value in cls.SETTINGS.items():
            existing = cls.query.filter_by(key=key).first()
            if existing:
                logger.info(f"   ✔️ '{key}' already exists with value: '{existing.value}'")
            else:
                logger.info(f"➕ Creating setting '{key}' with default value: '{default_value}'")
                db.session.add(cls(key=key, value=default_value))

        db.session.commit()
        logger.info(" Setting check complete. All required settings are now in the database")

    @classmethod
    def get_value(cls, key: str, fallback: str = None) -> str:
        """Retrieve the current value for a setting, with fallback."""
        logger.info(f"Getting value for setting '{key}'")
        setting = cls.query.filter_by(key=key).first()
        if setting:
            logger.info(f"🔎 Found '{key}' = '{setting.value}'")
            return setting.value
        default = cls.SETTINGS.get(key, fallback)
        logger.info(f"❓ Setting '{key}' not in DB. Returning default/fallback: '{default}'")
        return default
