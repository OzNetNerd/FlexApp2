# app/models/setting.py

from sqlalchemy import inspect

from app.models.base import BaseModel, db
from app.utils.app_logging import get_logger

logger = get_logger()


class Setting(BaseModel):
    __tablename__ = "settings"

    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    SETTINGS = {
        "debug_mode": "false",
        "maintenance_mode": "false",
        "feature_x_enabled": "true",
    }

    def __repr__(self) -> str:
        return f"<Setting {self.key!r}: {self.value!r}>"

    @classmethod
    def seed(cls) -> None:
        """Ensure all app settings exist in the DB with defaults if needed."""
        inspector = inspect(db.engine)
        logger.info(f"🔧 Checking for existence of {cls.__tablename__!r} table")

        if cls.__tablename__ not in inspector.get_table_names():
            logger.warning(f"⚠️ Table {cls.__tablename__!r} does not exist. Creating")
            db.create_all()
            logger.info(f"Table {cls.__tablename__!r} created successfully.")

        logger.info("🔍 Verifying required settings in the database")

        for key, default_value in cls.SETTINGS.items():
            existing = cls.query.filter_by(key=key).first()
            if existing:
                logger.info(f"   ✔️ {key!r} already exists with value: {existing.value!r}")
            else:
                logger.info(f"➕ Creating setting {key!r} with default value: {default_value!r}")
                db.session.add(cls(key=key, value=default_value))

        db.session.commit()
        logger.info(" Setting check complete. All required settings are now in the database")

    @classmethod
    def get_value(cls, key: str, fallback: str = None) -> str:
        """Retrieve the current value for a setting, with fallback."""
        logger.info(f"Getting value for setting {key!r}")
        setting = cls.query.filter_by(key=key).first()
        if setting:
            logger.info(f"🔎 Found {key!r} = {setting.value!r}")
            return setting.value
        default = cls.SETTINGS.get(key, fallback)
        logger.info(f"❓ Setting {key!r} not in DB. Returning default/fallback: {default!r}")
        return default
