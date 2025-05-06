"""
Card management routes for the SRS system.

This module contains routes for adding, editing, and managing SRS cards.
"""
from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.routes.web.pages.srs.blueprint import srs_bp, srs_service, DEFAULT_EASE_FACTOR
from app.routes.web.pages.srs.contexts import SRSAddCardContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.utils.app_logging import get_logger, log_message_and_variables

logger = get_logger()


@srs_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_card():
    """Add a new flashcard.

    GET: Display the form for adding a new card
    POST: Process the form submission and create a new card

    Returns:
        GET: HTML form for adding a card
        POST: Redirect to dashboard or add another card form
    """
    if request.method == "POST":
        logger.info(f"User {current_user.id} submitting new card")
        # Get form data
        category = request.form.get("category")
        question = request.form.get("question")
        answer = request.form.get("answer")
        tags = request.form.get("tags", "").strip()
        review_immediately = "review_immediately" in request.form
        action = request.form.get("action", "save")

        logger.info(f"New card data: category={category}, review_immediately={review_immediately}, action={action}")

        # Validate required fields
        if not all([category, question, answer]):
            logger.warning("Card creation missing required fields")
            flash("Please fill out all required fields", "error")
            return redirect(url_for("srs_bp.add_card"))

        # Create new card
        new_card = {
            "notable_type": category,
            "question": question,
            "answer": answer,
            "tags": [tag.strip() for tag in tags.split(",")] if tags else [],
            "ease_factor": DEFAULT_EASE_FACTOR,
            "interval": 0,
            "review_count": 0,
            "successful_reps": 0,
            "created_at": datetime.now(ZoneInfo("UTC")),
            "updated_at": datetime.now(ZoneInfo("UTC")),
        }

        # Set review date to today if immediate review requested
        if review_immediately:
            logger.info("Setting card for immediate review")
            new_card["next_review_at"] = datetime.now(ZoneInfo("UTC"))
        else:
            # Set review date to tomorrow by default
            logger.info("Setting card for review tomorrow")
            new_card["next_review_at"] = datetime.now(ZoneInfo("UTC")).replace(hour=0, minute=0, second=0,
                                                                               microsecond=0) + timedelta(
                days=1
            )

        # Save the card
        card = srs_service.create(new_card)
        logger.info(f"Card created successfully with ID {card.id}")

        flash("Card added successfully", "success")

        # Handle different save actions
        if action == "save_add_another":
            logger.info("Redirecting to add another card")
            return redirect(url_for("srs_bp.add_card"))
        else:
            logger.info("Redirecting to dashboard after card creation")
            return redirect(url_for("srs_bp.dashboard"))

    # GET request - show form
    logger.info(f"User {current_user.id} accessing add card form")

    # Get categories (decks) for dropdown
    logger.info("Retrieving categories for dropdown")
    categories = srs_service.get_categories()

    # Get stats for footer
    logger.info("Retrieving stats for form footer")
    stats = srs_service.get_stats()

    logger.info("Rendering add card form")

    context = SRSAddCardContext(categories=categories, stats=stats)

    config = RenderSafelyConfig(
        template_path="pages/srs/add_card.html",
        context=context,
        error_message="Failed to render add card form",
        endpoint_name="srs_bp.add_card"
    )

    return render_safely(config)


@srs_bp.route("/categories/create", methods=["POST"])
@login_required
def create_category():
    """Create a new category (deck) and return to the form.

    Process the form submission to create a new category and redirect
    back to the add card form.

    Returns:
        Redirect to the add card form
    """
    logger.info(f"User {current_user.id} creating new category")
    name = request.form.get("name")
    color = request.form.get("color", "#0d6efd")

    logger.info(f"New category data: name={name}, color={color}")

    if not name:
        logger.warning("Category creation missing required name field")
        flash("Category name is required", "error")
        return redirect(url_for("srs_bp.add_card"))

    category = srs_service.create_category(name, color)
    logger.info(f"Category '{name}' created successfully with ID {category.id}")
    flash(f"Category '{name}' created successfully", "success")

    return redirect(url_for("srs_bp.add_card"))