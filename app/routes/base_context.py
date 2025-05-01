from app.utils.app_logging import get_logger

logger = get_logger()

class BaseContext:
    """Base context class for all contexts (API and web)."""

    def __init__(self, **kwargs):
        """Initialize with common attributes for all contexts."""
        # Set all kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
            logger.debug(f"Set attribute '{key}' = {value}")

    def __repr__(self):
        """Return a detailed string representation of the context."""
        attributes = ", ".join(f"{key}={repr(value)}" for key, value in vars(self).items() if not key.startswith("_"))
        return f"{self.__class__.__name__}({attributes})"

    def __str__(self):
        """Return a user-friendly string representation of the context."""
        return f"{self.__class__.__name__}()"

    def to_dict(self):
        """Convert context to dictionary for template rendering or response serialization."""
        return {key: value for key, value in vars(self).items() if not key.startswith("_")}