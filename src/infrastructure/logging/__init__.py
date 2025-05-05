"""Logging package for the application.

This package provides utilities for configuring and using logging
throughout the application.
"""

from .config import configure_logging, get_logger

__all__ = ['configure_logging', 'get_logger']