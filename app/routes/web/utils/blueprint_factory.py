from typing import Any, Optional, Dict, Type
from dataclasses import dataclass, field
from flask import Blueprint

from app.routes.web.utils.route_registration import register_crud_routes, CrudRouteConfig
from app.services.service_base import CRUDService
from app.routes.web.utils.template_config import TemplateConfig
from app.utils.app_logging import get_logger

logger = get_logger()


@dataclass
class ViewConfig:
    """Configuration for a view."""
    view_class: Type
    kwargs: Dict[str, Any] = field(default_factory=dict)
    url: str = "/"
    endpoint: Optional[str] = None
    methods: Optional[list] = None


@dataclass
class BlueprintConfig:
    """Configuration class for creating CRUD blueprints."""
    model_class: Any
    service: Optional[Any] = None
    url_prefix: Optional[str] = None
    template_config: Optional[TemplateConfig] = None
    form_class: Optional[Any] = None
    views: Optional[Dict[str, ViewConfig]] = None

    def __post_init__(self):
        if self.template_config is None:
            self.template_config = TemplateConfig(model_class=self.model_class)
        if self.views is None:
            self.views = {}


def create_crud_blueprint(config: BlueprintConfig) -> Blueprint:
    """Creates a Flask Blueprint with CRUD routes and additional views."""
    model_class = config.model_class
    blueprint_name = f"{model_class.__tablename__}_bp"
    prefix = config.url_prefix if config.url_prefix is not None else f"/{model_class.__tablename__}"
    blueprint = Blueprint(blueprint_name, __name__, url_prefix=prefix)

    # Create default service if none provided
    service = config.service
    if service is None:
        service = CRUDService(model_class)

    # Register CRUD routes
    route_config = CrudRouteConfig(
        blueprint=blueprint,
        entity_table_name=model_class.__entity_name__,
        service=service,
        model_class=model_class,
        template_config=config.template_config,
        form_class=config.form_class,
    )
    register_crud_routes(route_config)

    # Register additional views
    for view_name, view_config in config.views.items():
        view_instance = view_config.view_class(
            blueprint=blueprint,
            service=service,
            **view_config.kwargs
        )
        view_instance.register(
            url=view_config.url,
            endpoint=view_config.endpoint or view_name,
            methods=view_config.methods
        )
        logger.info(f"Registered view {view_name} at {view_config.url}")

    return blueprint