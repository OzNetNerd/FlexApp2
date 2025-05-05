"""Factory for creating CRUD blueprints.

This module provides factories for creating Flask blueprints with
standardized CRUD operations for domain models.
"""

from typing import Any, Optional
from dataclasses import dataclass

from flask import Blueprint

from src.infrastructure.flask.template_config import TemplateConfig
from src.infrastructure.logging import get_logger
from src.interfaces.web.routes.crud_routes import register_crud_routes, CrudRouteConfig
from domain.shared.interfaces.repository import BaseRepository

logger = get_logger(__name__)


@dataclass
class BlueprintConfig:
    """Configuration for creating CRUD blueprints.

    Attributes:
        model_class: The model class to create routes for.
        service: Optional service for handling model operations.
        url_prefix: Optional URL prefix for the blueprint.
        template_config: Optional template configuration.
    """
    model_class: Any
    service: Optional[Any] = None
    url_prefix: Optional[str] = None
    template_config: Optional[TemplateConfig] = None

    def __post_init__(self):
        """Initialize default template configuration if not provided."""
        if self.template_config is None:
            self.template_config = TemplateConfig(model_class=self.model_class)


def create_crud_blueprint(config: BlueprintConfig) -> Blueprint:
    """Create a Flask Blueprint with CRUD routes for a domain model.

    Args:
        config: Blueprint configuration.

    Returns:
        Configured Flask Blueprint.
    """
    model_class = config.model_class
    blueprint_name = f"{model_class.__tablename__}_bp"
    prefix = config.url_prefix if config.url_prefix is not None else f"/{model_class.__tablename__}"
    blueprint = Blueprint(blueprint_name, __name__, url_prefix=prefix)

    # Create default service if none provided
    service = config.service
    if service is None:
        # In DDD, this would be replaced with a proper repository or application service
        service = BaseRepository(model_class)

    route_config = CrudRouteConfig(
        blueprint=blueprint,
        entity_table_name=model_class.__entity_name__,
        service=service,
        model_class=model_class,
        template_config=config.template_config,
    )

    register_crud_routes(route_config)
    return blueprint