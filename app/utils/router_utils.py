# app/routes/routers/router_utils.py

import importlib
import pkgutil
from typing import Any, Callable, Iterator, List, Optional

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
        exclusions: Optional[List[str]] = None
) -> None:
    """Generic blueprint registration with customizable behavior."""
    modules = list(discover_modules(package_path, exclusions))

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