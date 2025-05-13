# app/routes/api/pages/srs.py

from flask import Blueprint

from app.routes.api.route_registration import ApiCrudRouteConfig
from app.services.srs import SRSService
from app.utils.app_logging import get_logger

logger = get_logger()

ENTITY_NAME = "SRS"
ENTITY_PLURAL_NAME = ENTITY_NAME

srs_api_bp = Blueprint(f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}")

srs_service = SRSService()

srs_api_crud_config = ApiCrudRouteConfig(blueprint=srs_api_bp, entity_table_name=ENTITY_NAME, service=srs_service)