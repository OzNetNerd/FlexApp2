import logging
from app.models.base import db, BaseModel

logger = logging.getLogger(__name__)


class Setting(BaseModel):
    """Represents application-level settings configured by users/admins."""

    __tablename__ = "settings"

    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Settings {self.key}: {self.value}>"

    def save(self) -> "Settings":
        logger.debug(f"Saving setting '{self.key}' with value '{self.value}'")
        super().save()
        logger.info(f"Setting '{self.key}' saved successfully.")
        return self

    def delete(self) -> None:
        logger.debug(f"Deleting setting '{self.key}'")
        super().delete()
        logger.info(f"Setting '{self.key}' deleted successfully.")
