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

def log_kwargs(**kwargs: dict) -> None:
    """Logs all keyword arguments in a dictionary.

    Args:
        kwargs: The dictionary of keyword arguments (typically **kwargs).
        title: A title to prefix the log block.
        exclude: List of keys to exclude from logging.
    """
    for key, value in kwargs.items():
        logger.info(f"  📝 {key}: {value}")
