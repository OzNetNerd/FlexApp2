"""
Batch operations for the SRS system.

This module contains routes for performing batch operations on cards,
such as batch review, reset, or deletion.
"""
from flask import request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from datetime import datetime
from zoneinfo import ZoneInfo
from app.routes.web.pages.srs.blueprint import srs_bp, srs_service, DEFAULT_EASE_FACTOR
from app.utils.app_logging import get_logger

logger = get_logger()


@srs_bp.route("/batch-action", methods=["POST"])
@login_required
def batch_action():
    """Perform batch actions on selected cards.

    Process batch actions such as review, reset, or delete on selected cards.

    Returns:
        Redirect to appropriate page based on the action
    """
    logger.info(f"User {current_user.id} performing batch action")
    selected_ids = request.form.getlist("selected_cards")
    action = request.form.get("batch_action")
    logger.info(f"Batch action: {action} on {len(selected_ids)} cards")

    if not selected_ids:
        logger.warning("Batch action attempted with no cards selected")
        flash("No cards were selected", "warning")
        return redirect(request.referrer or url_for("srs_bp.dashboard"))

    if action == "review":
        # Start review session with selected cards
        logger.info(f"Starting batch review with {len(selected_ids)} cards")
        session["review_queue"] = selected_ids
        return redirect(url_for("srs_bp.review_batch"))
    elif action == "reset":
        # Reset progress for selected cards
        logger.info(f"Resetting progress for {len(selected_ids)} cards")
        for card_id in selected_ids:
            card = srs_service.get_by_id(int(card_id))
            if card:
                logger.info(f"Resetting card {card_id}")
                update_data = {
                    "interval": 0,
                    "ease_factor": DEFAULT_EASE_FACTOR,
                    "review_count": 0,
                    "successful_reps": 0,
                    "next_review_at": datetime.now(ZoneInfo("UTC")),
                    "last_reviewed_at": None,
                    "last_rating": None,
                }
                srs_service.update(card, update_data)
        flash(f"Reset progress for {len(selected_ids)} cards", "success")
    elif action == "delete":
        # Delete selected cards
        logger.info(f"Deleting {len(selected_ids)} cards")
        count = 0
        for card_id in selected_ids:
            card = srs_service.get_by_id(int(card_id))
            if card:
                logger.info(f"Deleting card {card_id}")
                card.delete()
                count += 1
        flash(f"Deleted {count} cards", "success")
        logger.info(f"Successfully deleted {count} cards")

    # Redirect back to previous page
    return redirect(request.referrer or url_for("srs_bp.dashboard"))