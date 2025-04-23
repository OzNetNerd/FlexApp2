from flask import Blueprint
from app.utils.app_logging import get_logger
from app.services.crud_service import CRUDService
from app.models import Contact
from app.routes.api.route_registration import ApiCrudRouteConfig

logger = get_logger()

ENTITY_NAME = "Contact"
ENTITY_PLURAL_NAME = "Contacts"

contacts_api_bp = Blueprint(
    f"{ENTITY_NAME.lower()}_api",
    __name__,
    url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}"
)

contact_service = CRUDService(Contact)

contact_api_crud_config = ApiCrudRouteConfig(
    blueprint=contacts_api_bp,
    entity_table_name=ENTITY_NAME,
    service=contact_service
)
