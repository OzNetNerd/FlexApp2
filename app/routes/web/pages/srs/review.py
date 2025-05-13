"""
Review routes for the SRS system.

This module contains routes for reviewing cards in the SRS system,
including individual and batch review functionality.
"""

from flask import request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.routes.web.pages.srs.blueprint import srs_bp, srs_service
from app.routes.web.pages.srs.contexts import SRSReviewContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.utils.app_logging import get_logger

logger = get_logger()


@srs_bp.route("/<int:item_id>/review", methods=["GET", "POST"])
@login_required
def review_item(item_id):
    """Web route for reviewing an SRS item.

    GET: Display the card for review
    POST: Process the review rating and schedule the next review

    Args:
        item_id (int): The ID of the card to review

    Returns:
        GET: HTML for the review page
        POST: Redirect to the next card or dashboard
    """
    logger.info(f"User {current_user.id} reviewing SRS item {item_id}")
    item = srs_service.get_by_id(item_id)
    is_batch = "batch" in request.args

    if not item:
        logger.warning(f"Card {item_id} not found during review attempt")
        flash("Card not found", "error")
        return redirect(url_for("srs_bp.dashboard"))

    if request.method == "POST":
        logger.info(f"Processing review submission for card {item_id}")
        rating = int(request.form.get("rating", 0))
        logger.info(f"Card {item_id} received rating: {rating}")
        item = srs_service.schedule_review(item_id, rating)

        flash("Card reviewed successfully", "success")

        # If this is part of a batch review, get next from session queue
        if is_batch and session.get("review_queue"):
            logger.info("Continuing batch review process")
            next_id = session["review_queue"][0]
            session["review_queue"] = session["review_queue"][1:]
            logger.info(f"Moving to next card in batch: {next_id}")
            return redirect(url_for("srs_bp.review_item", item_id=next_id, batch=True))
        elif is_batch and not session.get("review_queue"):
            logger.info("Batch review completed")
            flash("You've completed the batch review!", "success")
            return redirect(url_for("srs_bp.dashboard"))

        # Otherwise handle as normal
        next_due = srs_service.get_next_due_item_id(item_id)
        if next_due:
            logger.info(f"Moving to next due card: {next_due}")
            return redirect(url_for("srs_bp.review_item", item_id=next_due))
        else:
            logger.info("No more due cards, returning to dashboard")
            return redirect(url_for("srs_bp.dashboard"))

    # Get navigation variables
    logger.info("Preparing review navigation variables")
    next_item_id = srs_service.get_next_due_item_id(item_id)
    prev_item_id = srs_service.get_prev_item_id(item_id)

    # Get remaining batch items count if this is a batch review
    remaining_count = len(session.get("review_queue", [])) + 1 if is_batch else 0

    logger.info(f"Rendering review page for card {item_id}")

    context = SRSReviewContext(
        card=item, next_item_id=next_item_id, prev_item_id=prev_item_id, is_batch=is_batch, remaining_count=remaining_count
    )

    config = RenderSafelyConfig(
        template_path="pages/srs/review.html",
        context=context,
        error_message="Failed to render review page",
        endpoint_name="srs_bp.review_item",
    )

    return render_safely(config)


@srs_bp.route("/strategy/<strategy>", methods=["GET"])
@login_required
def review_by_strategy(strategy):
    """Start a review session using a specific review strategy.

    Retrieves cards based on the specified strategy and sets up a batch review session.

    Args:
        strategy (str): The review strategy to use

    Returns:
        Redirect to the first card in the batch review
    """
    logger.info(f"User {current_user.id} starting review with strategy: {strategy}")
    valid_strategies = ["due_mix", "priority_first", "hard_cards_first", "mastery_boost", "struggling_focus", "new_mix"]
    if strategy not in valid_strategies:
        logger.warning(f"Invalid review strategy requested: {strategy}")
        flash(f"Invalid review strategy: {strategy}", "error")
        return redirect(url_for("srs_bp.dashboard"))

    # Get cards based on strategy
    cards = srs_service.get_review_strategy(strategy, limit=20)
    logger.info(f"Retrieved {len(cards)} cards for strategy {strategy}")

    if not cards:
        logger.info(f"No cards available for strategy {strategy}")
        flash("No cards available for this review strategy", "warning")
        return redirect(url_for("srs_bp.dashboard"))

    # Store card IDs in session for review
    session["review_queue"] = [card.id for card in cards]
    logger.info(f"Created review queue with {len(cards)} cards")

    strategy_names = {
        "due_mix": "Mixed Categories Review",
        "priority_first": "Overdue First Review",
        "hard_cards_first": "Difficult Cards Focus",
        "mastery_boost": "Mastery Boost Review",
        "struggling_focus": "Struggling Cards Focus",
        "new_mix": "New & Due Cards Mix",
    }

    # Set session variable for strategy name to display during review
    session["review_strategy"] = strategy_names[strategy]
    logger.info(f"Beginning batch review with strategy: {strategy_names[strategy]}")

    # Redirect to first card in queue
    return redirect(url_for("srs_bp.review_item", item_id=cards[0].id, batch=True))


@srs_bp.route("/review-batch", methods=["GET"])
@login_required
def review_batch():
    """Review a batch of selected cards.

    Starts a review session for cards that were previously selected
    in a batch action and stored in the session.

    Returns:
        Redirect to the first card in the batch review
    """
    logger.info(f"User {current_user.id} starting batch review")
    # Get queue from session
    review_queue = session.get("review_queue", [])

    if not review_queue:
        logger.warning("Batch review attempted with empty queue")
        flash("No cards in review queue", "warning")
        return redirect(url_for("srs_bp.dashboard"))

    # Get first card ID and remove from queue
    card_id = review_queue[0]
    session["review_queue"] = review_queue[1:]
    logger.info(f"Starting batch review with card {card_id}, {len(review_queue) - 1} remaining")

    return redirect(url_for("srs_bp.review_item", item_id=card_id, batch=True))
