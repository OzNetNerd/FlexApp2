# app/routes/web/blueprint_factory.py

from typing import Any, Optional
from flask import Blueprint

from app.routes.web.route_registration import default_crud_templates, register_crud_routes, CrudRouteConfig
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()


def create_crud_blueprint(model_class: Any, service: Optional[Any] = None, url_prefix: Optional[str] = None) -> Blueprint:
    """Creates a Flask Blueprint with CRUD routes for a database model.

    Args:
        model_class: SQLAlchemy model class that defines __tablename__ and __entity_name__
        service: Optional service instance to handle CRUD operations
        url_prefix: Optional custom URL prefix (default uses model's tablename)

    Returns:
        Flask Blueprint with all CRUD routes registered
    """
    blueprint_name = f"{model_class.__tablename__}_bp"
    # Use custom URL prefix if provided, otherwise use tablename
    prefix = url_prefix if url_prefix is not None else f"/{model_class.__tablename__}"
    blueprint = Blueprint(blueprint_name, __name__, url_prefix=prefix)

    # Create default service if none provided
    if service is None:
        service = CRUDService(model_class)

    templates = default_crud_templates(model_class)
    config = CrudRouteConfig(blueprint=blueprint, entity_table_name=model_class.__entity_name__, service=service,
                             templates=templates)

    register_crud_routes(config)
    return blueprint
