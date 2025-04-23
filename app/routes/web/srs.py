# app/routes/web/srs.py

from flask import Blueprint
from app.utils.app_logging import get_logger
from app.services.srs_service import SRSService
from app.models import SRSItem
from app.routes.web.route_registration import CrudRouteConfig, default_crud_templates

logger = get_logger()

srs_bp = Blueprint("srs_bp", __name__, url_prefix="/srs")
srs_service = SRSService()
templates = default_crud_templates("SRSItem")

srs_crud_config = CrudRouteConfig(
    blueprint=srs_bp,
    entity_table_name="SRSItem",
    service=srs_service,
    templates=templates,
)
