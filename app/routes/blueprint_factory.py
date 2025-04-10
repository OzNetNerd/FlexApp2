# blueprint_factory.py

from flask import Blueprint
import logging

logger = logging.getLogger(__name__)


def create_blueprint(name, import_name=None, url_prefix=None):
    """
    Factory function to create blueprints with consistent naming and configuration.

    Args:
        name (str): Name of the blueprint
        import_name (str, optional): Import name for the blueprint. Defaults to the blueprint name.
        url_prefix (str, optional): URL prefix for the blueprint. Defaults to "/name".

    Returns:
        Blueprint: Configured Flask blueprint
    """
    if import_name is None:
        import_name = f"app.routes.{name}"

    if url_prefix is None:
        url_prefix = f"/{name.replace('_', '-')}"

    logger.info(f"Creating blueprint: {name} with prefix {url_prefix}")
    blueprint = Blueprint(name, import_name, url_prefix=url_prefix)
    return blueprint
