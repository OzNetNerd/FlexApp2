"""
Filtering routes for the SRS system.

This module contains routes for filtering and categorizing cards
in various ways, including by due date, category, learning stage,
difficulty, and performance.
"""
from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from zoneinfo import ZoneInfo
from app.routes.web.pages.srs.blueprint import srs_bp, srs_service
from app.routes.web.pages.srs.contexts import (
    SRSCardListContext,
    SRSCategoryContext,
    SRSFilteredCardsContext,
    SRSFilteredContext
)
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.utils.app_logging import get_logger, log_message_and_variables

logger = get_logger()


@srs_bp.route("/due", methods=["GET"])
@login_required
def due_cards():
    """View all cards due for review today.

    Returns:
        HTML: The rendered due cards template
    """
    logger.info(f"User {current_user.id} viewing all due cards")
    cards = srs_service.get_due_cards()
    logger.info(f"Retrieved {len(cards)} due cards")

    context = SRSCardListContext(
        title="Cards Due Today",
        cards=cards
    )

    config = RenderSafelyConfig(
        template_path="pages/srs/due.html",
        context=context,
        error_message="Failed to render due cards page",
        endpoint_name="srs_bp.due_cards"
    )

    return render_safely(config)


@srs_bp.route("/category/<string:category_type>", methods=["GET"])
@login_required
def category_view(category_type):
    """View cards by category.

    Display all cards belonging to a specific category.

    Args:
        category_type (str): The type of category to filter by

    Returns:
        HTML: The rendered category view template
    """
    logger.info(f"User {current_user.id} viewing cards in category: {category_type}")
    cards = srs_service.get_by_type(category_type)
    logger.info(f"Retrieved {len(cards)} cards in category {category_type}")

    category_info = {
        "company": {"name": "Companies", "color": "primary"},
        "contact": {"name": "Contacts", "color": "success"},
        "opportunity": {"name": "Opportunities", "color": "danger"},
    }

    info = category_info.get(category_type, {"name": "Unknown", "color": "secondary"})
    logger.info(f"Rendering category view for {info['name']}")

    context = SRSCategoryContext(
        cards=cards,
        category_type=category_type,
        category_name=info["name"],
        category_color=info["color"]
    )

    config = RenderSafelyConfig(
        template_path="pages/srs/category.html",
        context=context,
        error_message=f"Failed to render category view for {category_type}",
        endpoint_name="srs_bp.category_view"
    )

    return render_safely(config)


@srs_bp.route("/learning-stage/<stage>", methods=["GET"])
@login_required
def cards_by_learning_stage(stage):
    """View cards by learning stage.

    Display cards filtered by their learning stage (new, learning, reviewing, mastered).

    Args:
        stage (str): The learning stage to filter by

    Returns:
        HTML: The rendered filtered cards template or redirect to dashboard
    """
    logger.info(f"User {current_user.id} filtering cards by learning stage: {stage}")
    valid_stages = ["new", "learning", "reviewing", "mastered"]
    if stage not in valid_stages:
        logger.warning(f"Invalid learning stage requested: {stage}")
        flash(f"Invalid learning stage: {stage}", "error")
        return redirect(url_for("srs_bp.dashboard"))

    cards = srs_service.get_cards_by_learning_stage(stage)
    logger.info(f"Retrieved {len(cards)} cards in learning stage {stage}")

    stage_names = {"new": "New Cards", "learning": "Learning Cards", "reviewing": "Review Cards",
                   "mastered": "Mastered Cards"}

    logger.info(f"Rendering filtered cards for learning stage: {stage_names[stage]}")

    context = SRSFilteredCardsContext(
        cards=cards,
        title=stage_names[stage],
        filters={"learning_stage": stage},
        category_counts=srs_service.count_by_type(),
        due_category_counts=srs_service.count_due_by_type(),
        due_today=srs_service.count_due_today(),
        total_cards=srs_service.count_total(),
        active_tab=stage
    )

    config = RenderSafelyConfig(
        template_path="pages/srs/filtered_cards.html",
        context=context,
        error_message=f"Failed to render cards by learning stage: {stage}",
        endpoint_name="srs_bp.cards_by_learning_stage"
    )

    return render_safely(config)


@srs_bp.route("/difficulty/<difficulty>", methods=["GET"])
@login_required
def cards_by_difficulty(difficulty):
    """View cards by difficulty level.

    Display cards filtered by their difficulty level (hard, medium, easy).

    Args:
        difficulty (str): The difficulty level to filter by

    Returns:
        HTML: The rendered filtered cards template or redirect to dashboard
    """
    logger.info(f"User {current_user.id} filtering cards by difficulty: {difficulty}")
    valid_difficulties = ["hard", "medium", "easy"]
    if difficulty not in valid_difficulties:
        logger.warning(f"Invalid difficulty level requested: {difficulty}")
        flash(f"Invalid difficulty level: {difficulty}", "error")
        return redirect(url_for("srs_bp.dashboard"))

    cards = srs_service.get_cards_by_difficulty(difficulty)
    logger.info(f"Retrieved {len(cards)} cards with difficulty {difficulty}")

    difficulty_names = {"hard": "Hard Cards", "medium": "Medium Difficulty Cards", "easy": "Easy Cards"}

    logger.info(f"Rendering filtered cards for difficulty: {difficulty_names[difficulty]}")

    context = SRSFilteredCardsContext(
        cards=cards,
        title=difficulty_names[difficulty],
        filters={"difficulty": difficulty},
        category_counts=srs_service.count_by_type(),
        due_category_counts=srs_service.count_due_by_type(),
        due_today=srs_service.count_due_today(),
        total_cards=srs_service.count_total(),
        active_tab=f"difficulty_{difficulty}"
    )

    config = RenderSafelyConfig(
        template_path="pages/srs/filtered_cards.html",
        context=context,
        error_message=f"Failed to render cards by difficulty: {difficulty}",
        endpoint_name="srs_bp.cards_by_difficulty"
    )

    return render_safely(config)


@srs_bp.route("/performance/<performance>", methods=["GET"])
@login_required
def cards_by_performance(performance):
    """View cards by performance level.

    Display cards filtered by their performance level (struggling, average, strong).

    Args:
        performance (str): The performance level to filter by

    Returns:
        HTML: The rendered filtered cards template or redirect to dashboard
    """
    logger.info(f"User {current_user.id} filtering cards by performance: {performance}")
    valid_performances = ["struggling", "average", "strong"]
    if performance not in valid_performances:
        logger.warning(f"Invalid performance level requested: {performance}")
        flash(f"Invalid performance level: {performance}", "error")
        return redirect(url_for("srs_bp.dashboard"))

    cards = srs_service.get_cards_by_performance(performance)
    logger.info(f"Retrieved {len(cards)} cards with performance {performance}")

    performance_names = {"struggling": "Struggling Cards", "average": "Average Performance Cards",
                         "strong": "Strong Performance Cards"}

    logger.info(f"Rendering filtered cards for performance: {performance_names[performance]}")

    context = SRSFilteredCardsContext(
        cards=cards,
        title=performance_names[performance],
        filters={"performance": performance},
        category_counts=srs_service.count_by_type(),
        due_category_counts=srs_service.count_due_by_type(),
        due_today=srs_service.count_due_today(),
        total_cards=srs_service.count_total(),
        active_tab=f"performance_{performance}"
    )

    config = RenderSafelyConfig(
        template_path="pages/srs/filtered_cards.html",
        context=context,
        error_message=f"Failed to render cards by performance: {performance}",
        endpoint_name="srs_bp.cards_by_performance"
    )

    return render_safely(config)


@srs_bp.route("/cards", methods=["GET"])
@login_required
def filtered_cards():
    """View cards with filtering options.

    Display cards with various filtering and sorting options.

    Returns:
        HTML: The rendered filtered cards template
    """
    logger.info(f"User {current_user.id} accessing filtered cards view")

    # Get filter parameters from request
    filters = {
        "due_only": "due_only" in request.args,
        "category": request.args.get("category"),
        "search": request.args.get("search"),
        "sort_by": request.args.get("sort_by", "next_review_at"),
        "sort_order": request.args.get("sort_order", "asc"),
    }
    logger.info(f"Applied filters: {filters}")

    # Advanced filters
    if request.args.get("min_interval"):
        filters["min_interval"] = float(request.args.get("min_interval"))
    if request.args.get("max_interval"):
        filters["max_interval"] = float(request.args.get("max_interval"))
    if request.args.get("min_ease"):
        filters["min_ease"] = float(request.args.get("min_ease"))
    if request.args.get("max_ease"):
        filters["max_ease"] = float(request.args.get("max_ease"))

    # Add a custom filter to handle None dates
    filters["handle_none_dates"] = True
    logger.info("Added None date handling to filters")

    # Get filtered cards
    cards = srs_service.get_filtered_cards(filters)
    logger.info(f"Retrieved {len(cards)} cards matching filter criteria")

    # Get category counts for sidebar
    logger.info("Getting category statistics for sidebar")
    category_counts = srs_service.count_by_type()
    due_category_counts = srs_service.count_due_by_type()

    # Count cards by learning stage
    logger.info("Getting learning stage and difficulty statistics")
    learning_stages = srs_service.get_learning_stages_counts()
    difficulty_counts = srs_service.get_difficulty_counts()
    performance_counts = srs_service.get_performance_counts()

    # Prepare template data
    context = SRSFilteredContext(
        cards=cards,
        filters=filters,
        category_counts=category_counts,
        due_category_counts=due_category_counts,
        due_today=srs_service.count_due_today(),
        total_cards=srs_service.count_total(),
        learning_stages=learning_stages,
        difficulty_counts=difficulty_counts,
        performance_counts=performance_counts,
        now=datetime.now(ZoneInfo("UTC"))
    )

    config = RenderSafelyConfig(
        template_path="pages/srs/filtered_cards.html",
        context=context,
        error_message="Failed to render filtered cards",
        endpoint_name="srs_bp.filtered_cards"
    )

    log_message_and_variables(f"📄 Vars being sent to template:", context.to_dict())
    logger.info(f"📄 Rendering template: {config.template_path}")
    return render_safely(config)