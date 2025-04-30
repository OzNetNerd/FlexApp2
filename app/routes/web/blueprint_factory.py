# app/routes/web/blueprint_factory.py

from typing import Any, Optional
from dataclasses import dataclass
from flask import Blueprint

from app.routes.web.route_registration import register_crud_routes, CrudRouteConfig
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger


logger = get_logger()


@dataclass
class BlueprintConfig:
    """Configuration class for creating CRUD blueprints."""
    model_class: Any
    service: Optional[Any] = None
    url_prefix: Optional[str] = None
    create_template: Optional[str] = None
    view_template: Optional[str] = None
    index_template: Optional[str] = None
    edit_template: Optional[str] = None

    def __post_init__(self):
        plural = self.model_class.__entity_plural__.lower()

        for attr, value in self.__dict__.items():
            if not attr.endswith('_template') or value is not None:
                continue

            if attr == 'index_template':
                setattr(self, attr, f"pages/{plural}/index.html")
            else:
                setattr(self, attr, f"pages/{plural}/view.html")


def create_crud_blueprint(config: BlueprintConfig) -> Blueprint:
    """Creates a Flask Blueprint with CRUD routes for a database model.

    Args:
        config: Configuration object containing all blueprint settings

    Returns:
        Flask Blueprint with all CRUD routes registered
    """
    model_class = config.model_class
    blueprint_name = f"{model_class.__tablename__}_bp"
    # Use custom URL prefix if provided, otherwise use tablename
    prefix = config.url_prefix if config.url_prefix is not None else f"/{model_class.__tablename__}"
    blueprint = Blueprint(blueprint_name, __name__, url_prefix=prefix)

    # Create default service if none provided
    service = config.service
    if service is None:
        service = CRUDService(model_class)

    route_config = CrudRouteConfig(
        blueprint=blueprint,
        entity_table_name=model_class.__entity_name__,
        service=service,
        model_class=model_class
    )

    # Set custom templates if provided
    if config.create_template:
        route_config.create_template = config.create_template
    if config.view_template:
        route_config.view_template = config.view_template
    if config.index_template:
        route_config.index_template = config.index_template
    if config.edit_template:
        route_config.edit_template = config.edit_template

    register_crud_routes(route_config)
    return blueprint