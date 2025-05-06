"""
Dashboard and statistics routes for the SRS system.

This module contains routes for the SRS dashboard and statistics pages.
"""
from flask import url_for
from flask_login import login_required, current_user
from app.routes.web.pages.srs.blueprint import srs_bp, srs_service
from app.routes.web.pages.srs.contexts import SRSDashboardContext, SRSContext
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.utils.app_logging import get_logger

logger = get_logger()


@srs_bp.route("/", methods=["GET"])
@login_required
def dashboard():
    """Render the flashcard dashboard.

    The dashboard provides an overview of the user's SRS system, including:
    - Summary statistics (total cards, due today, success rate, etc.)
    - Card categories with counts and progress information
    - Due cards for today (limited to 5 for display)
    - Learning progress data for a chart

    Returns:
        HTML: The rendered dashboard template
    """
    logger.info(f"User {current_user.id} accessing SRS dashboard")

    # Get summary statistics
    logger.info("Collecting dashboard statistics")
    stats = {
        "total_cards": srs_service.count_total(),
        "due_today": srs_service.count_due_today(),
        "success_rate": srs_service.calculate_success_rate(),
        "days_streak": srs_service.get_streak_days(),
        "weekly_reviews": srs_service.count_weekly_reviews(),
        "mastered_cards": srs_service.count_mastered_cards_this_month(),
        "retention_increase": srs_service.calculate_retention_increase(),
        "perfect_reviews": srs_service.count_consecutive_perfect_reviews(),
    }

    # Get card categories with counts
    logger.info("Getting card categories with counts")
    categories = [
        {
            "name": "Companies",
            "type": "company",
            "icon": "building",
            "color": "primary",
            "total": srs_service.count_by_type("company"),
            "due": srs_service.count_due_by_type("company"),
            "progress": srs_service.calculate_progress_by_type("company"),
        },
        {
            "name": "Contacts",
            "type": "contact",
            "icon": "people",
            "color": "success",
            "total": srs_service.count_by_type("contact"),
            "due": srs_service.count_due_by_type("contact"),
            "progress": srs_service.calculate_progress_by_type("contact"),
        },
        {
            "name": "Opportunities",
            "type": "opportunity",
            "icon": "graph-up-arrow",
            "color": "danger",
            "total": srs_service.count_by_type("opportunity"),
            "due": srs_service.count_due_by_type("opportunity"),
            "progress": srs_service.calculate_progress_by_type("opportunity"),
        },
    ]

    # Get due cards for today (limited to 5 for display)
    logger.info("Getting due cards for dashboard display")
    due_cards = srs_service.get_due_cards(limit=5)

    # Get learning progress data for chart
    logger.info("Retrieving learning progress data for chart")
    progress_data = srs_service.get_learning_progress_data(months=7)

    logger.info("Rendering SRS dashboard")
    context = SRSDashboardContext(
        stats=stats,
        categories=categories,
        due_cards=due_cards,
        progress_data=progress_data
    )

    config = RenderSafelyConfig(
        template_path="pages/srs/dashboard.html",
        context=context,
        error_message="Failed to render SRS dashboard",
        endpoint_name="srs_bp.dashboard"
    )

    return render_safely(config)


@srs_bp.route("/stats", methods=["GET"])
@login_required
def statistics():
    """View detailed learning statistics.

    This route provides detailed statistics about the user's learning
    progress, including retention rates, learning efficiency, and more.

    Returns:
        HTML: The rendered statistics template
    """
    logger.info(f"User {current_user.id} viewing detailed learning statistics")
    stats = srs_service.get_detailed_stats()
    logger.info("Retrieved detailed SRS statistics")

    context = SRSContext(title="Learning Statistics")
    context.stats = stats

    config = RenderSafelyConfig(
        template_path="pages/srs/stats.html",
        context=context,
        error_message="Failed to render statistics page",
        endpoint_name="srs_bp.statistics"
    )

    return render_safely(config)