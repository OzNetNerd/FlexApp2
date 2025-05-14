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


def create_crud_blueprint(config):
    """Create a blueprint with CRUD routes based on configuration."""
    blueprint_name = f"{config.model_class.__tablename__}_bp"
    blueprint = Blueprint(blueprint_name, __name__, url_prefix=config.url_prefix)

    # Register views
    for endpoint, view_config in config.views.items():
        view_class = view_config.view_class
        url = view_config.url or f"/{endpoint}"
        endpoint_name = view_config.endpoint or endpoint

        # Pass the service and other kwargs to the view
        kwargs = view_config.kwargs or {}
        kwargs['service'] = config.service

        # Register the view with the blueprint
        view_class.register(
            blueprint=blueprint,
            url=url,
            endpoint=endpoint_name,
            kwargs=kwargs
        )

    crud_config = CrudRouteConfig(
        blueprint=blueprint,
        entity_table_name=config.model_class.__tablename__,
        service=config.service,
        model_class=config.model_class,
        template_config=config.template_config,
        form_class=config.form_class
    )
    register_crud_routes(crud_config)

    return blueprint