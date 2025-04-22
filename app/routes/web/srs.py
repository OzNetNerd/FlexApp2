# web/srs.py

import logging
from datetime import datetime
from flask import Blueprint, flash, redirect, url_for
from flask_login import login_required

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
    view="pages/crud/create_view_edit_srs_item.html",
    edit="pages/crud/create_view_edit_srs_item.html",
)

config = CrudRouteConfig(
    blueprint=srs_bp,
    entity_table_name="SRSItem",
    service=srs_service,
    templates=templates,
)
register_crud_routes(config)


@srs_bp.route('/review/<int:item_id>', methods=['GET'])
@login_required
def review_item(item_id):
    current_item = srs_service.get_by_id(item_id)

    if not current_item:
        flash("Card not found", "danger")
        return redirect(url_for('web.srs.index'))

    # Get all due items
    due_items = srs_service.get_due_items()

    # Find current item index and determine next/prev
    try:
        current_index = [item.id for item in due_items].index(item_id)
        total_cards = len(due_items)
        next_item_id = due_items[(current_index + 1) % total_cards].id if total_cards > 0 else None
        prev_item_id = due_items[(current_index - 1) % total_cards].id if total_cards > 0 else None
    except ValueError:
        current_index = 0
        total_cards = 0
        next_item_id = None
        prev_item_id = None

    # Get stats
    stats = {
        'total_cards': SRSItem.query.count(),
        'cards_due': SRSItem.query.filter(SRSItem.next_review_at <= datetime.utcnow()).count(),
        'cards_reviewed_today': ReviewHistory.query.filter(
            ReviewHistory.created_at >= datetime.today().replace(hour=0, minute=0, second=0)
        ).count()
    }

    # Create EntityContext
    context = EntityContext(
        action="review",
        entity=current_item,
        entity_table_name="SRSItem",
        entity_id=item_id,
        title="Review Card",
        read_only=True,
        blueprint_name="srs_bp",  # Use the actual blueprint name
        current_index=current_index + 1,
        total_cards=total_cards,
        next_item_id=next_item_id,
        prev_item_id=prev_item_id,
        stats=stats
    )

    config = RenderSafelyConfig(
        template_path='pages/crud/view_srs_item.html',
        context=context,
        error_message="Error loading flashcard",
        endpoint="srs_bp.index"  # Use the actual blueprint endpoint
    )

    return render_safely(config)