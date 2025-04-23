from flask import Blueprint
from app.utils.app_logging import get_logger
from app.services.crud_service import CRUDService
from app.models import Opportunity
from app.routes.api.route_registration import ApiCrudRouteConfig

logger = get_logger()

ENTITY_NAME = "Opportunity"
ENTITY_PLURAL_NAME = "Opportunities"

opportunities_api_bp = Blueprint(
    f"{ENTITY_NAME.lower()}_api",
    __name__,
    url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}"
)

opportunity_service = CRUDService(Opportunity)

opportunity_api_crud_config = ApiCrudRouteConfig(
    blueprint=opportunities_api_bp,
    entity_table_name=ENTITY_NAME,
    service=opportunity_service
)
