import importlib
import pkgutil
from typing import Any, Iterator

from flask import Blueprint, Flask

from app.routes.web.route_registration import CrudRouteConfig, register_crud_routes
from app.utils.app_logging import get_logger

logger = get_logger()


def discover_web_modules() -> Iterator[Any]:
    """Yield all modules in the app.routes.web package, excluding the components subpackage."""
    package = importlib.import_module("app.routes.web")
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if module_name == "components":
            continue
        yield importlib.import_module(f"{package.__name__}.{module_name}")


def register_web_blueprints(app: Flask) -> None:
    """Auto-wire CRUD routes and register all web blueprints."""
    # Phase 1: register CRUD routes for each CrudRouteConfig
    for module in discover_web_modules():
        for attr in dir(module):
            if attr.endswith("_crud_config"):
                config = getattr(module, attr)
                if isinstance(config, CrudRouteConfig):
                    logger.debug(f"Wiring web CRUD routes for {config.entity_table_name}")
                    register_crud_routes(config)

    # Phase 2: register blueprints on the Flask app
    for module in discover_web_modules():
        for attr in dir(module):
            if attr.endswith("_bp"):
                bp = getattr(module, attr)
                if isinstance(bp, Blueprint):
                    logger.debug(f"Registering web blueprint: {bp.name} at {bp.url_prefix}")
                    app.register_blueprint(bp)
