# app/routes/web/blueprint_factory.py

from typing import Any, Optional
from dataclasses import dataclass
from flask import Blueprint

from app.routes.web.route_registration import register_crud_routes, CrudRouteConfig
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger
from app.routes.web.template_config import TemplateConfig


logger = get_logger()


@dataclass
class BlueprintConfig:
    """Configuration class for creating CRUD blueprints."""

    model_class: Any
    service: Optional[Any] = None
    url_prefix: Optional[str] = None
    template_config: Optional[TemplateConfig] = None

    def __post_init__(self):
        if self.template_config is None:
            self.template_config = TemplateConfig(model_class=self.model_class)


def create_crud_blueprint(config: BlueprintConfig) -> Blueprint:
    """Creates a Flask Blueprint with CRUD routes for a database model."""
    model_class = config.model_class
    blueprint_name = f"{model_class.__tablename__}_bp"
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
        model_class=model_class,
        template_config=config.template_config,
    )

    register_crud_routes(route_config)
    return blueprint
