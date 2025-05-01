from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.models.pages.srs import SRS
from app.services.srs_service import SRSService
from app.routes.web.blueprint_factory import create_crud_blueprint, BlueprintConfig
from app.utils.app_logging import get_logger, log_message_and_vars

logger = get_logger()

# Define missing constant
DEFAULT_EASE_FACTOR = 2.5

# Create the service instance
logger.info("Initializing SRS service")
srs_service = SRSService()

# Create the blueprint config
logger.info("Creating SRS blueprint configuration")
srs_config = BlueprintConfig(
    model_class=SRS,
    service=srs_service,
    create_template="pages/srs/create.html"
)

# Create the blueprint using the config
logger.info("Creating SRS blueprint")
srs_bp = create_crud_blueprint(srs_config)


# Dashboard route
@srs_bp.route("/dashboard", methods=["GET"])
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
    return render_template("pages/srs/dashboard.html", stats=stats, categories=categories, due_cards=due_cards,
                           progress_data=progress_data)


# Due cards route
@srs_bp.route("/due", methods=["GET"])
@login_required
def due_cards():
    """View all cards due for review today."""
    logger.info(f"User {current_user.id} viewing all due cards")
    cards = srs_service.get_due_cards()
    logger.info(f"Retrieved {len(cards)} due cards")
    return render_template("pages/srs/due.html", cards=cards, title="Cards Due Today")


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
    return render_template(
        "pages/srs/review.html",
        card=item,
        title="Review Card",
        next_item_id=next_item_id,
        prev_item_id=prev_item_id,
        is_batch=is_batch,
        remaining_count=remaining_count,
    )


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

    return render_template(
        "pages/srs/category.html",
        cards=cards,
        category_type=category_type,
        category_name=info["name"],
        category_color=info["color"],
        title=f"{info['name']} Cards",
    )


# Statistics route
@srs_bp.route("/stats", methods=["GET"])
@login_required
def statistics():
    """View detailed learning statistics."""
    logger.info(f"User {current_user.id} viewing detailed learning statistics")
    stats = srs_service.get_detailed_stats()
    logger.info("Retrieved detailed SRS statistics")
    return render_template("pages/srs/stats.html", stats=stats, title="Learning Statistics")


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
    return render_template(
        "pages/srs/filtered_cards.html",
        cards=cards,
        title=stage_names[stage],
        filters={"learning_stage": stage},
        category_counts=srs_service.count_by_type(),
        due_category_counts=srs_service.count_due_by_type(),
        due_today=srs_service.count_due_today(),
        total_cards=srs_service.count_total(),
        active_tab=stage,
    )


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
    return render_template(
        "pages/srs/filtered_cards.html",
        cards=cards,
        title=difficulty_names[difficulty],
        filters={"difficulty": difficulty},
        category_counts=srs_service.count_by_type(),
        due_category_counts=srs_service.count_due_by_type(),
        due_today=srs_service.count_due_today(),
        total_cards=srs_service.count_total(),
        active_tab=f"difficulty_{difficulty}",
    )


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
    return render_template(
        "pages/srs/filtered_cards.html",
        cards=cards,
        title=performance_names[performance],
        filters={"performance": performance},
        category_counts=srs_service.count_by_type(),
        due_category_counts=srs_service.count_due_by_type(),
        due_today=srs_service.count_due_today(),
        total_cards=srs_service.count_total(),
        active_tab=f"performance_{performance}",
    )


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
    template_data = {
        "cards": cards,
        "title": "Filtered Cards",
        "filters": filters,
        "category_counts": category_counts,
        "due_category_counts": due_category_counts,
        "due_today": srs_service.count_due_today(),
        "total_cards": srs_service.count_total(),
        "learning_stages": learning_stages,
        "difficulty_counts": difficulty_counts,
        "performance_counts": performance_counts,
        "now": datetime.now(ZoneInfo("UTC")),
    }

    template_name = "pages/srs/filtered_cards.html"
    log_message_and_vars(f"📄 Vars being sent to template:", template_data)
    logger.info(f"📄 Rendering template: {template_name}")
    return render_template(template_name, **template_data)



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
                                                                   microsecond=0) + timedelta(days=1)

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
    return render_template("pages/srs/add_card.html", title="Add New Card", categories=categories, stats=stats)


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