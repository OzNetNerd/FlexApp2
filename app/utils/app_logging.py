import logging

logger = logging.getLogger(__name__)

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