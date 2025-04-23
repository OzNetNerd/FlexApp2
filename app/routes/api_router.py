# app/routes/api_router.py

import importlib
import pkgutil
from typing import Any, Iterator

from flask import Blueprint, Flask

from app.routes.api.route_registration import register_api_crud_routes
from app.utils.app_logging import get_logger

logger = get_logger()


def discover_api_modules() -> Iterator[Any]:
    """Yield all modules in the app.routes.api package."""
    package = importlib.import_module("app.routes.api")
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        yield importlib.import_module(f"{package.__name__}.{module_name}")


def register_api_blueprints(app: Flask) -> None:
    """Auto-register API blueprints with their CRUD routes.

    1. Discover all `*_api_crud_config` in app.routes.api and call
       register_api_crud_routes(config) on each blueprint.
    2. Discover all `*_api_bp` and register each Blueprint on the app.
    """
    modules = list(discover_api_modules())

    # 1) Wire up CRUD routes on each blueprint
    for module in modules:
        for attr in dir(module):
            if attr.endswith("_api_crud_config"):
                config = getattr(module, attr)
                logger.debug(f"Wiring CRUD routes for {config.entity_table_name}")
                register_api_crud_routes(config)

    # 2) Register all auto-discovered blueprints
    for module in modules:
        for attr in dir(module):
            if attr.endswith("_api_bp"):
                bp: Blueprint = getattr(module, attr)
                logger.debug(f"Registering API blueprint: {bp.name} @ {bp.url_prefix}")
                app.register_blueprint(bp)
