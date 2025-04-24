# app/routes/web/blueprint_factory.py

from flask import Blueprint

from app.routes.web.route_registration import (
    default_crud_templates,
    register_crud_routes,
    CrudRouteConfig
)
from app.services.crud_service import CRUDService
from app.utils.app_logging import get_logger

logger = get_logger()


def create_crud_blueprint(model_class):
    blueprint_name = f"{model_class.__tablename__}_bp"
    blueprint = Blueprint(blueprint_name, __name__, url_prefix=f"/{model_class.__tablename__}")

    service = CRUDService(model_class)
    templates = default_crud_templates(model_class.__entity_name__)
    config = CrudRouteConfig(
        blueprint=blueprint,
        entity_table_name=model_class.__entity_name__,
        service=service,
        templates=templates
    )

    register_crud_routes(config)
    return blueprint
