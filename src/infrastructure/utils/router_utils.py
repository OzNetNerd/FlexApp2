# src/infrastructure/utils/router_utils.py

import importlib
import pkgutil
from typing import Callable, List, Optional

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

    Args:
        app: The Flask application instance
        package_path: Dot-notation path to package containing blueprint modules
        config_suffix: Suffix for configuration variables in modules
        register_func: Function to call for registering routes
        blueprint_suffix: Suffix for blueprint variables to discover
        exclusions: List of module names to exclude from registration

    Returns:
        None
    """
    exclusions = exclusions or []
    package = importlib.import_module(package_path)

    # Iterate through all modules in the package
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if module_name in exclusions:
            continue

        # Import the module
        module_path = f"{package_path}.{module_name}"
        module = importlib.import_module(module_path)

        # Find blueprint variables in the module
        for name in dir(module):
            if name.endswith(blueprint_suffix):
                blueprint = getattr(module, name)
                app.register_blueprint(blueprint)

                # Find corresponding config and register routes if exists
                config_name = name.replace(blueprint_suffix, config_suffix)
                if hasattr(module, config_name):
                    config = getattr(module, config_name)
                    register_func(blueprint, config)