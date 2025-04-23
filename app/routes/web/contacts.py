# app/routes/web/contacts.py

from flask import Blueprint
from app.utils.app_logging import get_logger
from app.services.crud_service import CRUDService
from app.models import Contact
from app.routes.web.route_registration import CrudRouteConfig, default_crud_templates

logger = get_logger()

contacts_bp = Blueprint("contacts_bp", __name__, url_prefix="/contacts")
contact_service = CRUDService(Contact)
templates = default_crud_templates("Contact")

contact_crud_config = CrudRouteConfig(
    blueprint=contacts_bp,
    entity_table_name="Contact",
    service=contact_service,
    templates=templates,
)
