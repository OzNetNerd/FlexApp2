# app/routes/web/opportunities.py

from flask import Blueprint
from app.utils.app_logging import get_logger
from app.services.crud_service import CRUDService
from app.models import Opportunity
from app.routes.web.route_registration import CrudRouteConfig, default_crud_templates

logger = get_logger()

opportunities_bp = Blueprint("opportunities_bp", __name__, url_prefix="/opportunities")
opportunity_service = CRUDService(Opportunity)
templates = default_crud_templates("Opportunity")

opportunity_crud_config = CrudRouteConfig(
    blueprint=opportunities_bp,
    entity_table_name="Opportunity",
    service=opportunity_service,
    templates=templates,
)
