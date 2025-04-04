import logging
from app.models.base import db, BaseModel

logger = logging.getLogger(__name__)


class Setting(BaseModel):
    """Represents application-level settings configured by code, editable via UI."""

    __tablename__ = "settings"

    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    # The authoritative list of settings used by the app
    SETTINGS = {
        "debug_mode": "false",
        "maintenance_mode": "false",
        "feature_x_enabled": "true",
    }

    def __repr__(self) -> str:
        return f"<Settings {self.key}: {self.value}>"

    def save(self) -> "Setting":
        logger.debug(f"Saving setting '{self.key}' with value '{self.value}'")
        super().save()
        logger.info(f"Setting '{self.key}' saved successfully.")
        return self

    def delete(self) -> None:
        logger.debug(f"Deleting setting '{self.key}'")
        super().delete()
        logger.info(f"Setting '{self.key}' deleted successfully.")

    @classmethod
    def seed(cls) -> None:
        """Insert known settings if not present, using default values."""
        for key, default_value in cls.SETTINGS.items():
            if not cls.query.filter_by(key=key).first():
                logger.info(f"Seeding setting '{key}' with default value '{default_value}'")
                db.session.add(cls(key=key, value=default_value))
        db.session.commit()

    @classmethod
    def get_value(cls, key: str, fallback: str = None) -> str:
        """Get the current value for a setting, falling back to default or provided fallback."""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            return setting.value
        return cls.SETTINGS.get(key, fallback)
