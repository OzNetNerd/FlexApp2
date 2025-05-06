from flask import request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.models.pages.srs import SRS
from app.services.srs_service import SRSService
from app.routes.web.utils.blueprint_factory import create_crud_blueprint, BlueprintConfig
from app.utils.app_logging import get_logger, log_message_and_variables
from app.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.utils.context import WebContext

logger = get_logger()

# Define missing constant
DEFAULT_EASE_FACTOR = 2.5

# Create the service instance
logger.info("Initializing SRS service")
srs_service = SRSService()

# Create the blueprint config
logger.info("Creating SRS blueprint configuration")
srs_config = BlueprintConfig(model_class=SRS, service=srs_service)

# Create the blueprint using the config
logger.info("Creating SRS blueprint")
srs_bp = create_crud_blueprint(srs_config)


# Custom context classes for SRS pages
class SRSContext(WebContext):
    """Base context for SRS pages."""

    def __init__(self, title="SRS", **kwargs):
        super().__init__(title=title, **kwargs)


class SRSCardListContext(SRSContext):
    """Context for pages displaying card lists."""

    def __init__(self, title, cards, **kwargs):
        super().__init__(title=title, **kwargs)
        self.cards = cards


class SRSDashboardContext(SRSContext):
    """Context for the SRS dashboard."""

    def __init__(self, stats, categories, due_cards, progress_data, **kwargs):
        super().__init__(title="SRS Dashboard", **kwargs)
        self.stats = stats
        self.categories = categories
        self.due_cards = due_cards
        self.progress_data = progress_data


# Dashboard route
@srs_bp.route("/", methods=["GET"])
@login_required
def dashboard():
    """Render the flashcard dashboard."""
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


# Due cards route
@srs_bp.route("/due", methods=["GET"])
@login_required
def due_cards():
    """View all cards due for review today."""
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


@srs_bp.route("/<int:item_id>/review", methods=["GET", "POST"])
@login_required
def review_item(item_id):
    """Web route for reviewing an SRS item."""
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

    class SRSReviewContext(SRSContext):
        def __init__(self, card, next_item_id, prev_item_id, is_batch, remaining_count):
            super().__init__(title="Review Card")
            self.card = card
            self.next_item_id = next_item_id
            self.prev_item_id = prev_item_id
            self.is_batch = is_batch
            self.remaining_count = remaining_count

    context = SRSReviewContext(
        card=item,
        next_item_id=next_item_id,
        prev_item_id=prev_item_id,
        is_batch=is_batch,
        remaining_count=remaining_count
    )

    config = RenderSafelyConfig(
        template_path="pages/srs/review.html",
        context=context,
        error_message="Failed to render review page",
        endpoint_name="srs_bp.review_item"
    )

    return render_safely(config)


# Category view route
@srs_bp.route("/category/<string:category_type>", methods=["GET"])
@login_required
def category_view(category_type):
    """View cards by category."""
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

    class SRSCategoryContext(SRSContext):
        def __init__(self, cards, category_type, category_name, category_color):
            super().__init__(title=f"{category_name} Cards")
            self.cards = cards
            self.category_type = category_type
            self.category_name = category_name
            self.category_color = category_color

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


# Statistics route
@srs_bp.route("/stats", methods=["GET"])
@login_required
def statistics():
    """View detailed learning statistics."""
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


@srs_bp.route("/learning-stage/<stage>", methods=["GET"])
@login_required
def cards_by_learning_stage(stage):
    """View cards by learning stage."""
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

    class SRSFilteredCardsContext(SRSContext):
        def __init__(self, cards, title, filters, category_counts, due_category_counts, due_today, total_cards,
                     active_tab):
            super().__init__(title=title)
            self.cards = cards
            self.filters = filters
            self.category_counts = category_counts
            self.due_category_counts = due_category_counts
            self.due_today = due_today
            self.total_cards = total_cards
            self.active_tab = active_tab

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
    """View cards by difficulty level."""
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
    """View cards by performance level."""
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


@srs_bp.route("/strategy/<strategy>", methods=["GET"])
@login_required
def review_by_strategy(strategy):
    """Start a review session using a specific review strategy."""
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


@srs_bp.route("/cards", methods=["GET"])
@login_required
def filtered_cards():
    """View cards with filtering options."""
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
    class SRSFilteredContext(SRSContext):
        def __init__(self, **kwargs):
            super().__init__(title="Filtered Cards", **kwargs)
            for key, value in kwargs.items():
                setattr(self, key, value)

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


@srs_bp.route("/batch-action", methods=["POST"])
@login_required
def batch_action():
    """Perform batch actions on selected cards."""
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


@srs_bp.route("/review-batch", methods=["GET"])
@login_required
def review_batch():
    """Review a batch of selected cards."""
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


@srs_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_card():
    """Add a new flashcard."""
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

    class SRSAddCardContext(SRSContext):
        def __init__(self, categories, stats):
            super().__init__(title="Add New Card")
            self.categories = categories
            self.stats = stats

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
    """Create a new category (deck) and return to the form."""
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