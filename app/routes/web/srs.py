# web/srs.py

import logging
from datetime import datetime
from flask import Blueprint

from app.routes.web.route_registration import (
    register_crud_routes,
    CrudRouteConfig,
    CrudTemplates,
    render_safely,
    RenderSafelyConfig,
)
from app.routes.web.context import EntityContext
from app.services.srs_service import SRSService
from app.models.srs_item import SRSItem
from app.models.review_history import ReviewHistory

logger = logging.getLogger(__name__)

srs_bp = Blueprint("srs_bp", __name__, url_prefix="/srs")
srs_service = SRSService()

templates = CrudTemplates(
    index="pages/tables/srs_items.html",
    create="pages/crud/create_view_edit_srs_item.html",
    view="pages/crud/view_srs_item.html",
    edit="pages/crud/create_view_edit_srs_item.html",
)

config = CrudRouteConfig(
    blueprint=srs_bp,
    entity_table_name="SRSItem",
    service=srs_service,
    templates=templates,
)
register_crud_routes(config)


@srs_bp.route("/review/<int:entity_id>", methods=["GET"])
def review_card(entity_id):
    item = srs_service.get_by_id(entity_id)

    # Get all due cards and determine next one (excluding current)
    due_cards = srs_service.get_due_items()
    next_card = next((card for card in due_cards if card.id != item.id), None)

    stats = {
        "total_cards": SRSItem.query.count(),
        "cards_due": len(due_cards),
        "cards_reviewed_today": ReviewHistory.query.filter(
            ReviewHistory.reviewed_at >= datetime.utcnow().date()
        ).count()
    }

    context = EntityContext(
        action="view",
        entity_table_name="SRSItem",
        entity=item,
        title="Review Card",
        read_only=True,
        extra_context={
            "stats": stats,
            "current_index": due_cards.index(item) + 1 if item in due_cards else 1,
            "total_cards": len(due_cards),
            "next_item_id": next_card.id if next_card else item.id,
        }
    )

    return render_safely(
        RenderSafelyConfig(
            template_path="pages/crud/view_srs_item.html",
            context=context,
            error_message="Failed to load review card",
            endpoint="review_card"
        )
    )
