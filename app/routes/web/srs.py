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
    logger.info(f"Loading review for SRSItem id={item_id}")
    current_item = srs_service.get_by_id(item_id)

    if not current_item:
        flash("Card not found", "danger")
        return redirect(url_for('srs_bp.index'))

    # Get all due items
    due_items = srs_service.get_due_items()
    logger.info(f"Found {len(due_items)} due items")

    # Default values - ALWAYS set these
    current_index = 0
    total_cards = len(due_items)
    next_item_id = item_id  # Default to current item
    prev_item_id = item_id  # Default to current item

    # Find current item index and determine next/prev
    try:
        if due_items:
            item_ids = [item.id for item in due_items]
            if item_id in item_ids:
                current_index = item_ids.index(item_id)
                if total_cards > 1:
                    next_item_id = due_items[(current_index + 1) % total_cards].id
                    prev_item_id = due_items[(current_index - 1) % total_cards].id

        logger.info(f"Navigation: current_index={current_index}, next_id={next_item_id}, prev_id={prev_item_id}")
    except Exception as e:
        logger.error(f"Error setting up navigation: {str(e)}", exc_info=True)

    # Get stats
    total_cards_count = SRSItem.query.count()
    cards_due_count = SRSItem.query.filter(SRSItem.next_review_at <= datetime.utcnow()).count()

    today_start = datetime.today().replace(hour=0, minute=0, second=0)
    cards_reviewed_today_count = ReviewHistory.query.filter(
        ReviewHistory.created_at >= today_start
    ).count()

    stats = {
        'total_cards': total_cards_count,
        'cards_due': cards_due_count,
        'cards_reviewed_today': cards_reviewed_today_count
    }

    logger.info(f"Stats: {stats}")

    # Create EntityContext
    context = EntityContext(
        action="review",
        entity=current_item,
        entity_table_name="SRSItem",
        entity_id=item_id,
        title="Review Card",
        read_only=True,
        blueprint_name="srs_bp",
        current_index=current_index + 1,
        total_cards=total_cards,
        next_item_id=next_item_id,
        prev_item_id=prev_item_id,
        stats=stats
    )

    config = RenderSafelyConfig(
        template_path='pages/crud/create_view_edit_srs_item.html',
        context=context,
        error_message="Error loading flashcard",
        endpoint="srs_bp.index"
    )

    return render_safely(config)