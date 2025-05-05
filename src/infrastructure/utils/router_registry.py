"""Utility module for blueprint registration across different interface types."""

from typing import Callable, List, Optional

from flask import Flask


def register_blueprint_routes(
    app: Flask,
    package_path: str,
    register_func: Callable,
    blueprint_suffix: str,
    config_suffix: str,
    exclusions: Optional[List[str]] = None,
) -> None:
    """Auto-discover and register blueprints with the Flask application.

    This function uses a convention-based approach to find and register
    Flask blueprints throughout the application based on naming conventions.

    Args:
        app: The Flask application instance.
        package_path: Dot-notation path to the package containing blueprints.
        register_func: Function to register routes with a blueprint.
        blueprint_suffix: Suffix for blueprint variables (e.g., '_bp').
        config_suffix: Suffix for configuration variables.
        exclusions: Optional list of module names to exclude from registration.
    """
    import importlib
    import inspect
    import pkgutil
    from types import ModuleType

    exclusions = exclusions or []

    def _register_from_module(module: ModuleType) -> None:
        """Register blueprints from a single module."""
        # Find blueprint objects and configurations in the module
        for name, obj in inspect.getmembers(module):
            # Register blueprints with naming convention
            if name.endswith(blueprint_suffix) and hasattr(obj, "register"):
                # Find matching config if it exists
                config_name = name.replace(blueprint_suffix, config_suffix)
                config = getattr(module, config_name, None)

                # Register routes with the blueprint
                if config:
                    register_func(obj, config)

                # Register blueprint with the Flask app
                app.register_blueprint(obj)

    def _explore_package(package_path: str) -> None:
        """Recursively explore package for blueprint modules."""
        try:
            package = importlib.import_module(package_path)
        except ImportError:
            return

        # Process current package's modules
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            # Skip excluded modules
            if any(excl in name for excl in exclusions):
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
