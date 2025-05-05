"""Configuration package for the application.

This package provides configuration classes and functionality for different
environments, making configuration management more maintainable and organized.
"""

from .base import BaseConfig, PROJECT_ROOT
from .environments import DevelopmentConfig, TestingConfig, ProductionConfig, ConfigFactory

# Re-export for convenience
config = ConfigFactory.get_config()

__all__ = ["BaseConfig", "DevelopmentConfig", "TestingConfig", "ProductionConfig", "ConfigFactory", "config", "PROJECT_ROOT"]
