from jinja2 import DebugUndefined
import logging

logger = logging.getLogger(__name__)


def configure_logging(level=logging.INFO) -> None:
    """Sets up basic logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info("✅ Logging is configured.")


def log_instance_vars(instance, exclude: list[str] = None) -> None:
    """Logs all instance variables of a class.

    Args:
        instance: The class instance.
        exclude: List of variable names to exclude from logging.
    """
    exclude = exclude or []
    logger.info(f"📋 Attributes for {instance.__class__.__name__}:")

    for attr, value in vars(instance).items():
        if attr in exclude:
            continue
        logger.info(f"  📝 {attr}: {value}")

    if exclude:
        logger.info(f"  ℹ️ (Excluded: {', '.join(exclude)})")
    else:
        logger.info("  ℹ️ (No exclusions)")

def log_kwargs(title: str, **kwargs: dict) -> None:
    """Logs all keyword arguments with a title and a warning icon for empty values.

    Args:
        title: A required title to display before logging the kwargs.
        kwargs: The dictionary of keyword arguments (typically **kwargs).
    """
    logger.info(f"📝 {title}")
    for key, value in kwargs.items():
        is_empty = not value and value is not False
        icon = "⚠️" if is_empty else "📝"
        logger.info(f"  {icon} {key}: {value!r}")


class LoggingUndefined(DebugUndefined):
    """Custom Jinja2 Undefined that logs access to undefined variables."""

    def _fail_with_undefined_error(self, *args, **kwargs):
        logger.error(f"❌ Undefined Jinja variable accessed: {self._undefined_name}")
        return super()._fail_with_undefined_error(*args, **kwargs)
