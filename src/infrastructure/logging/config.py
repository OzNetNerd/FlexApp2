"""Logging configuration module.

This module provides utilities for configuring application logging
with different handlers and formatters based on the environment.
"""

import logging
import os
import sys
from typing import Dict, Any, Optional

from ..config import config


def configure_logging(app_name: str = "app") -> logging.Logger:
    """Configure and return a logger with appropriate handlers and formatters.

    Args:
        app_name: The name of the application/logger. Defaults to "app".

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create logger
    logger = logging.getLogger(app_name)

    # Set log level based on environment
    log_level = logging.DEBUG if config.DEBUG else logging.INFO
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()

    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Create a formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    # Optionally add file handler for production
    if os.environ.get("FLASK_ENV") == "production":
        file_handler = create_file_handler(log_level, formatter)
        if file_handler:
            logger.addHandler(file_handler)

    return logger


def create_file_handler(log_level: int, formatter: logging.Formatter) -> Optional[logging.Handler]:
    """Create a file handler for logging to a file.

    Args:
        log_level: The logging level for the handler.
        formatter: The formatter to use for log messages.

    Returns:
        Optional[logging.Handler]: File handler if log directory exists,
            None otherwise.
    """
    log_dir = os.environ.get("LOG_DIR")
    if not log_dir:
        return None

    try:
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Create file handler
        file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        return file_handler
    except (IOError, OSError):
        # If there's an error creating the file handler, return None
        return None


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance.

    If name is None, returns the root app logger.
    Otherwise, returns a child logger with the specified name.

    Args:
        name: The name of the logger. If None, returns the root app logger.
            If specified, returns a child logger with the name "app.{name}".

    Returns:
        logging.Logger: Configured logger instance.
    """
    app_name = "app"

    # Get or create the root app logger
    if name:
        logger_name = f"{app_name}.{name}"
    else:
        logger_name = app_name

    # If the root logger hasn't been configured yet, configure it
    root_logger = logging.getLogger(app_name)
    if not root_logger.handlers:
        configure_logging(app_name)

    return logging.getLogger(logger_name)
