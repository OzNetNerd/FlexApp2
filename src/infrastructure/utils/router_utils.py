# src/infrastructure/utils/router_utils.py

import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Callable, List, Optional, Any

from flask import Flask


def register_blueprint_routes(
    app: Flask,
    package_path: str,
    config_suffix: str,
    register_func: Callable,
    blueprint_suffix: str,
    exclusions: Optional[List[str]] = None,
) -> None:
    """Register blueprint routes based on a convention-based discovery approach.

    This utility function implements a flexible, convention-based approach to
    discover and register Flask blueprints from a specified package path.
    It recursively explores all subpackages to find blueprints.

    Args:
        app: The Flask application instance
        package_path: Dot-notation path to package containing blueprint modules
        config_suffix: Suffix for configuration variables in modules
        register_func: Function to call for registering routes
        blueprint_suffix: Suffix for blueprint variables to discover
        exclusions: List of module names to exclude from registration
    """
    exclusions = exclusions or []

    def _register_from_module(module: ModuleType) -> None:
        """Register blueprints from a single module."""
        for name, obj in inspect.getmembers(module):
            if name.endswith(blueprint_suffix) and hasattr(obj, "register"):
                app.register_blueprint(obj)

                # Find corresponding config and register routes if exists
                config_name = name.replace(blueprint_suffix, config_suffix)
                if hasattr(module, config_name):
                    config = getattr(module, config_name)
                    register_func(obj, config)

    def _explore_package(current_path: str) -> None:
        """Recursively explore package for blueprint modules."""
        try:
            package = importlib.import_module(current_path)
        except ImportError:
            return

        # Process current package modules
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            module_name = name.split(".")[-1]
            if any(excl in module_name for excl in exclusions):
                continue

            if is_pkg:
                # Recursively process subpackages
                _explore_package(name)
            else:
                # Process modules for blueprints
                try:
                    module = importlib.import_module(name)
                    _register_from_module(module)
                except ImportError:
                    continue

    # Start the recursive registration process
    _explore_package(package_path)
