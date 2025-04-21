import logging
from flask import Blueprint

from app.routes.web.route_registration import register_crud_routes, CrudRouteConfig, CrudTemplates
from app.services.srs_service import SRSService

logger = logging.getLogger(__name__)

srs_bp = Blueprint("srs_bp", __name__, url_prefix="/srs")

srs_service = SRSService()

templates = CrudTemplates(
    index="pages/tables/srs_items.html",
    create="pages/crud/create_view_edit_srs_item.html",
    view="pages/crud/view_srs_item.html",
    edit="pages/crud/create_view_edit_srs_item.html",
    # update/delete use defaults if you don't override
)

config = CrudRouteConfig(
    blueprint=srs_bp,
    entity_table_name="SRSItem",
    service=srs_service,
    templates=templates,
)
register_crud_routes(config)
