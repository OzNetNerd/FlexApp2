# app/utils/router_utils.py

import importlib
import pkgutil
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

from flask import Blueprint, Flask

from app.utils.app_logging import get_logger

logger = get_logger()


def discover_modules(package_path: str, exclusions: Optional[List[str]] = None) -> Iterator[Any]:
    """Yield all modules in the given package path, excluding any specified subpackages."""
    exclusions = exclusions or []
    package = importlib.import_module(package_path)
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        if module_name in exclusions:
            continue
        yield importlib.import_module(f"{package_path}.{module_name}")


def register_blueprint_routes(
        app: Flask,
        package_path: str,
        config_suffix: str,
        register_func: Callable,
        blueprint_suffix: str = "_bp",
        exclusions: Optional[List[str]] = None,
        return_blueprints: bool = False,
) -> Optional[Dict[str, Blueprint]]:
    """Generic blueprint registration with customizable behavior.

    Args:
        app: The Flask application instance
        package_path: Dot-notation path to the package containing blueprints
        config_suffix: Suffix for configuration objects
        register_func: Function to register routes with a blueprint
        blueprint_suffix: Suffix for blueprint objects
        exclusions: List of module names to exclude
        return_blueprints: If True, return a dictionary of {name: blueprint}

    Returns:
        Dictionary of discovered blueprints if return_blueprints is True, otherwise None
    """
    modules = list(discover_modules(package_path, exclusions))
    discovered_blueprints = {}

    # Phase 1: Configure routes
    for module in modules:
        for attr in dir(module):
            if attr.endswith(config_suffix):
                config = getattr(module, attr)
                logger.debug(f"Wiring routes for {getattr(config, 'entity_table_name', attr)}")
                register_func(config)

    # Phase 2: Register blueprints
    for module in modules:
        for attr in dir(module):
            if attr.endswith(blueprint_suffix):
                bp = getattr(module, attr)
                if isinstance(bp, Blueprint):
                    logger.debug(f"Registering blueprint: {bp.name} @ {bp.url_prefix}")
                    app.register_blueprint(bp)
                    discovered_blueprints[attr] = bp

    return discovered_blueprints if return_blueprints else None


def auto_discover_routes(package_path: str, recursive: bool = False) -> None:
    """Auto-import all modules in a package to register their route decorators.

    This function imports all modules in a package, which causes any route
    decorators (@blueprint.route) to be executed, registering the routes
    with their respective blueprints.

    Args:
        package_path: Dot-notation path to the package containing route modules
        recursive: If True, recursively discover modules in subpackages
    """
    package = importlib.import_module(package_path)
    logger.debug(f"Auto-discovering routes in package: {package_path}")

    if recursive:
        # Recursively walk through all submodules
        for _, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
            try:
                logger.debug(f"Importing module: {name}")
                importlib.import_module(name)
            except ImportError as e:
                logger.error(f"Error importing {name}: {e}")
    else:
        # Only discover modules in the immediate package
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
            if not is_pkg:  # Only import modules, not subpackages
                try:
                    logger.debug(f"Importing module: {name}")
                    importlib.import_module(name)
                except ImportError as e:
                    logger.error(f"Error importing {name}: {e}")


def recursive_discover_routes(package_path: str, bp_suffix: str = "_bp") -> None:
    """Recursively discover and import all route modules in a package hierarchy.

    This function first imports the package itself, then finds all blueprint modules
    and their corresponding route modules, ensuring all routes are registered.

    Args:
        package_path: Dot-notation path to the base package
        bp_suffix: Suffix used for blueprint variables
    """
    logger.info(f"Recursively discovering routes in: {package_path}")

    # First, import the package itself
    package = importlib.import_module(package_path)

    # Look for blueprint modules
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
        try:
            # Import the module/package
            module = importlib.import_module(module_name)

            # If it's a package, recurse into it to find routes
            if is_pkg:
                recursive_discover_routes(module_name, bp_suffix)

            # Look for blueprint objects in the module
            for attr_name in dir(module):
                if attr_name.endswith(bp_suffix) and isinstance(getattr(module, attr_name), Blueprint):
                    # Found a blueprint, now import all Python files in its directory
                    if is_pkg:
                        # If the blueprint is in a package, import all modules in that package
                        for _, route_module_name, _ in pkgutil.iter_modules(module.__path__, module.__name__ + '.'):
                            try:
                                logger.debug(f"Importing route module: {route_module_name}")
                                importlib.import_module(route_module_name)
                            except ImportError as e:
                                logger.error(f"Error importing route module {route_module_name}: {e}")

                    # Blueprint found in the module itself, it's already imported
                    logger.debug(f"Found blueprint: {attr_name} in {module_name}")

        except ImportError as e:
            logger.error(f"Error importing {module_name}: {e}")


def discover_blueprint_packages(package_path: str, bp_suffix: str = "_bp", exclusions: Optional[List[str]] = None) -> \
Dict[str, tuple]:
    """Discover all blueprint packages and their modules.

    Returns a dictionary of blueprint names and their modules.
    """
    exclusions = exclusions or []
    blueprints = {}
    package = importlib.import_module(package_path)

    # Look for blueprint modules
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
        # Skip excluded modules
        if any(excl in module_name for excl in exclusions):
            continue

        try:
            # Import the module/package
            module = importlib.import_module(module_name)

            # If it's a package, recurse
            if is_pkg:
                sub_blueprints = discover_blueprint_packages(module_name, bp_suffix, exclusions)
                blueprints.update(sub_blueprints)

            # Look for blueprint objects in the module
            for attr_name in dir(module):
                if attr_name.endswith(bp_suffix) and isinstance(getattr(module, attr_name), Blueprint):
                    bp = getattr(module, attr_name)
                    blueprints[attr_name] = (bp, module_name if is_pkg else None)
                    logger.debug(f"Found blueprint: {attr_name} in {module_name}")

        except ImportError as e:
            logger.error(f"Error importing {module_name}: {e}")

    return blueprints


def register_application_blueprints(
        app: Flask,
        package_path: str,
        root_blueprint: Optional[Blueprint] = None,
        config_suffix: Optional[str] = None,
        register_func: Optional[Callable] = None,
        blueprint_suffix: str = "_bp",
        exclusions: Optional[List[str]] = None,
) -> None:
    """Unified blueprint registration for both API and web endpoints.

    Args:
        app: The Flask application instance
        package_path: Dot-notation path to the package containing blueprints
        root_blueprint: Optional root blueprint to nest all discovered blueprints under
        config_suffix: Optional suffix for configuration objects (for API CRUD routes)
        register_func: Optional function to register routes with a blueprint
        blueprint_suffix: Suffix for blueprint objects
        exclusions: List of module names to exclude
    """
    logger.info(f"Discovering blueprints in: {package_path}")

    # First discover all blueprints and their packages
    blueprints = discover_blueprint_packages(
        package_path=package_path,
        bp_suffix=blueprint_suffix,
        exclusions=exclusions
    )

    logger.info(f"Discovered {len(blueprints)} blueprints")

    # Configure routes if needed (for API CRUD routes)
    if config_suffix and register_func:
        for bp_name, (_, module_path) in blueprints.items():
            if module_path:
                module = importlib.import_module(module_path)
                for attr in dir(module):
                    if attr.endswith(config_suffix):
                        config = getattr(module, attr)
                        logger.debug(f"Wiring routes for {getattr(config, 'entity_table_name', attr)}")
                        register_func(config)

    # Import all route modules before registering blueprints
    for bp_name, (_, module_path) in blueprints.items():
        if module_path:
            # Import all modules in the blueprint's package to register routes
            for _, route_module_name, _ in pkgutil.iter_modules(
                    importlib.import_module(module_path).__path__,
                    module_path + '.'
            ):
                try:
                    logger.debug(f"Importing route module: {route_module_name}")
                    importlib.import_module(route_module_name)
                except ImportError as e:
                    logger.error(f"Error importing route module {route_module_name}: {e}")

    # Now register the blueprints after their routes are defined
    for bp_name, (blueprint, _) in blueprints.items():
        if root_blueprint:
            logger.debug(f"Registering nested blueprint: {blueprint.name} @ {blueprint.url_prefix}")
            root_blueprint.register_blueprint(blueprint)
        else:
            logger.debug(f"Registering blueprint: {blueprint.name} @ {blueprint.url_prefix}")
            app.register_blueprint(blueprint)

    # Register the root blueprint with the app if provided
    if root_blueprint:
        logger.debug(f"Registering root blueprint: {root_blueprint.name} @ {root_blueprint.url_prefix}")
        app.register_blueprint(root_blueprint)

    logger.info(f"Blueprints and routes registered successfully for {package_path}")