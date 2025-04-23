import pkgutil
import importlib
from typing import Iterator, Any
from flask import Flask, Blueprint
from app.utils.app_logging import get_logger

logger = get_logger()


def discover_web_modules() -> Iterator[Any]:
    """Yield all modules in the app.routes.web package, excluding the components subpackage.

    Scans the `app.routes.web` directory and imports each module except those
    under `components`, yielding the imported module object.

    Returns:
        Iterator[Any]: Imported module objects.
    """
    package = importlib.import_module("app.routes.web")
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        if module_name == "components":
            continue
        yield importlib.import_module(f"{package.__name__}.{module_name}")


def register_web_blueprints(app: Flask) -> None:
    """Auto-register all web blueprints from app.routes.web.

    Discovers Blueprint objects named `<something>_bp` in each module
    returned by `discover_web_modules()` and registers them on the Flask app.

    Args:
        app (Flask): The Flask application instance.
    """
    for module in discover_web_modules():
        for attr in dir(module):
            if attr.endswith("_bp"):
                bp = getattr(module, attr)
                if isinstance(bp, Blueprint):
                    logger.debug(f"Registering web blueprint: {bp.name} at {bp.url_prefix}")
                    app.register_blueprint(bp)
