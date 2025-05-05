# src/infrastructure/logging.py

"""
Application logging configuration.

This module provides utilities for configuring and accessing application loggers.
"""

import logging
from logging import INFO, Formatter, StreamHandler


def configure_logging(app):
    """
    Configure application-wide logging.

    Args:
        app: Flask application instance.
    """
    # Configure console logging at INFO level
    console_handler = StreamHandler()
    console_handler.setLevel(INFO)
    console_handler.setFormatter(Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    root_logger = logging.getLogger()
    root_logger.setLevel(INFO)
    root_logger.addHandler(console_handler)

    logger = get_logger()
    logger.info("Configured console logging at INFO level")


def get_logger():
    """
    Get the application logger.

    Returns:
        Logger: The application logger instance.
    """
    return logging.getLogger("app")
