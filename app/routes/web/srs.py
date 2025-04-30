from flask import  render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from datetime import datetime, UTC
from app.models.pages.srs import SRS
from app.services.srs_service import SRSService
from app.routes.web.blueprint_factory import create_crud_blueprint, BlueprintConfig

# Create the service instance
srs_service = SRSService()

# Create the blueprint config
srs_config = BlueprintConfig(
    model_class=SRS,
    service=srs_service,
    create_template="pages/srs/create.html"
)

# Create the blueprint using the config
srs_bp = create_crud_blueprint(srs_config)# Specify custom create template


# Dashboard route
@srs_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """Render the flashcard dashboard."""
    # Get summary statistics
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
    due_cards = srs_service.get_due_cards(limit=5)

    # Get learning progress data for chart
    progress_data = srs_service.get_learning_progress_data(months=7)

    return render_template("pages/srs/dashboard.html", stats=stats, categories=categories, due_cards=due_cards, progress_data=progress_data)


# Due cards route
@srs_bp.route("/due", methods=["GET"])
@login_required
def due_cards():
    """View all cards due for review today."""
    cards = srs_service.get_due_cards()
    return render_template("pages/srs/due.html", cards=cards, title="Cards Due Today")


@srs_bp.route("/<int:item_id>/review", methods=["GET", "POST"])
@login_required
def review_item(item_id):
    """Web route for reviewing an SRS item."""
    item = srs_service.get_by_id(item_id)
    is_batch = "batch" in request.args

    if not item:
        flash("Card not found", "error")
        return redirect(url_for("srs_bp.dashboard"))

    if request.method == "POST":
        rating = int(request.form.get("rating", 0))
        item = srs_service.schedule_review(item_id, rating)

        flash("Card reviewed successfully", "success")

        # If this is part of a batch review, get next from session queue
        if is_batch and session.get("review_queue"):
            next_id = session["review_queue"][0]
            session["review_queue"] = session["review_queue"][1:]
            return redirect(url_for("srs_bp.review_item", item_id=next_id, batch=True))
        elif is_batch and not session.get("review_queue"):
            flash("You've completed the batch review!", "success")
            return redirect(url_for("srs_bp.dashboard"))

        # Otherwise handle as normal
        next_due = srs_service.get_next_due_item_id(item_id)
        if next_due:
            return redirect(url_for("srs_bp.review_item", item_id=next_due))
        else:
            return redirect(url_for("srs_bp.dashboard"))

    # Get navigation variables
    next_item_id = srs_service.get_next_due_item_id(item_id)
    prev_item_id = srs_service.get_prev_item_id(item_id)

    # Get remaining batch items count if this is a batch review
    remaining_count = len(session.get("review_queue", [])) + 1 if is_batch else 0

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
    cards = srs_service.get_by_type(category_type)

    category_info = {
        "company": {"name": "Companies", "color": "primary"},
        "contact": {"name": "Contacts", "color": "success"},
        "opportunity": {"name": "Opportunities", "color": "danger"},
    }

    info = category_info.get(category_type, {"name": "Unknown", "color": "secondary"})

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
    stats = srs_service.get_detailed_stats()
    return render_template("pages/srs/stats.html", stats=stats, title="Learning Statistics")


@srs_bp.route("/learning-stage/<stage>", methods=["GET"])
@login_required
def cards_by_learning_stage(stage):
    """View cards by learning stage."""
    valid_stages = ["new", "learning", "reviewing", "mastered"]
    if stage not in valid_stages:
        flash(f"Invalid learning stage: {stage}", "error")
        return redirect(url_for("srs_bp.dashboard"))

    cards = srs_service.get_cards_by_learning_stage(stage)

    stage_names = {"new": "New Cards", "learning": "Learning Cards", "reviewing": "Review Cards", "mastered": "Mastered Cards"}

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
    valid_difficulties = ["hard", "medium", "easy"]
    if difficulty not in valid_difficulties:
        flash(f"Invalid difficulty level: {difficulty}", "error")
        return redirect(url_for("srs_bp.dashboard"))

    cards = srs_service.get_cards_by_difficulty(difficulty)

    difficulty_names = {"hard": "Hard Cards", "medium": "Medium Difficulty Cards", "easy": "Easy Cards"}

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
    valid_performances = ["struggling", "average", "strong"]
    if performance not in valid_performances:
        flash(f"Invalid performance level: {performance}", "error")
        return redirect(url_for("srs_bp.dashboard"))

    cards = srs_service.get_cards_by_performance(performance)

    performance_names = {"struggling": "Struggling Cards", "average": "Average Performance Cards", "strong": "Strong Performance Cards"}

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
    valid_strategies = ["due_mix", "priority_first", "hard_cards_first", "mastery_boost", "struggling_focus", "new_mix"]
    if strategy not in valid_strategies:
        flash(f"Invalid review strategy: {strategy}", "error")
        return redirect(url_for("srs_bp.dashboard"))

    # Get cards based on strategy
    cards = srs_service.get_review_strategy(strategy, limit=20)

    if not cards:
        flash("No cards available for this review strategy", "warning")
        return redirect(url_for("srs_bp.dashboard"))

    # Store card IDs in session for review
    session["review_queue"] = [card.id for card in cards]

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

    # Redirect to first card in queue
    return redirect(url_for("srs_bp.review_item", item_id=cards[0].id, batch=True))


@srs_bp.route("/cards", methods=["GET"])
@login_required
def filtered_cards():
    """View cards with filtering options."""
    # Get filter parameters from request
    filters = {
        "due_only": "due_only" in request.args,
        "category": request.args.get("category"),
        "search": request.args.get("search"),
        "sort_by": request.args.get("sort_by", "next_review_at"),
        "sort_order": request.args.get("sort_order", "asc"),
    }

    # Advanced filters
    if request.args.get("min_interval"):
        filters["min_interval"] = float(request.args.get("min_interval"))
    if request.args.get("max_interval"):
        filters["max_interval"] = float(request.args.get("max_interval"))
    if request.args.get("min_ease"):
        filters["min_ease"] = float(request.args.get("min_ease"))
    if request.args.get("max_ease"):
        filters["max_ease"] = float(request.args.get("max_ease"))

    # Get filtered cards
    cards = srs_service.get_filtered_cards(filters)

    # Get category counts for sidebar
    category_counts = srs_service.count_by_type()
    due_category_counts = srs_service.count_due_by_type()

    # Count cards by learning stage
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
        "now": datetime.now(UTC),  # For comparing with due dates
    }

    return render_template("pages/srs/filtered_cards.html", **template_data)


@srs_bp.route("/batch-action", methods=["POST"])
@login_required
def batch_action():
    """Perform batch actions on selected cards."""
    selected_ids = request.form.getlist("selected_cards")
    action = request.form.get("batch_action")

    if not selected_ids:
        flash("No cards were selected", "warning")
        return redirect(request.referrer or url_for("srs_bp.dashboard"))

    if action == "review":
        # Start review session with selected cards
        session["review_queue"] = selected_ids
        return redirect(url_for("srs_bp.review_batch"))
    elif action == "reset":
        # Reset progress for selected cards
        for card_id in selected_ids:
            card = srs_service.get_by_id(int(card_id))
            if card:
                update_data = {
                    "interval": 0,
                    "ease_factor": DEFAULT_EASE_FACTOR,
                    "review_count": 0,
                    "successful_reps": 0,
                    "next_review_at": datetime.now(UTC),
                    "last_reviewed_at": None,
                    "last_rating": None,
                }
                srs_service.update(card, update_data)
        flash(f"Reset progress for {len(selected_ids)} cards", "success")
    elif action == "delete":
        # Delete selected cards
        count = 0
        for card_id in selected_ids:
            card = srs_service.get_by_id(int(card_id))
            if card:
                card.delete()
                count += 1
        flash(f"Deleted {count} cards", "success")

    # Redirect back to previous page
    return redirect(request.referrer or url_for("srs_bp.dashboard"))


@srs_bp.route("/review-batch", methods=["GET"])
@login_required
def review_batch():
    """Review a batch of selected cards."""
    # Get queue from session
    review_queue = session.get("review_queue", [])

    if not review_queue:
        flash("No cards in review queue", "warning")
        return redirect(url_for("srs_bp.dashboard"))

    # Get first card ID and remove from queue
    card_id = review_queue[0]
    session["review_queue"] = review_queue[1:]

    return redirect(url_for("srs_bp.review_item", item_id=card_id, batch=True))


@srs_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_card():
    """Add a new flashcard."""
    if request.method == "POST":
        # Get form data
        category = request.form.get("category")
        question = request.form.get("question")
        answer = request.form.get("answer")
        tags = request.form.get("tags", "").strip()
        review_immediately = "review_immediately" in request.form
        action = request.form.get("action", "save")

        # Validate required fields
        if not all([category, question, answer]):
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
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

        # Set review date to today if immediate review requested
        if review_immediately:
            new_card["next_review_at"] = datetime.now(UTC)
        else:
            # Set review date to tomorrow by default
            new_card["next_review_at"] = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        # Save the card
        card = srs_service.create(new_card)

        flash("Card added successfully", "success")

        # Handle different save actions
        if action == "save_add_another":
            return redirect(url_for("srs_bp.add_card"))
        else:
            return redirect(url_for("srs_bp.dashboard"))

    # GET request - show form
    # Get categories (decks) for dropdown
    categories = srs_service.get_categories()

    # Get stats for footer
    stats = srs_service.get_stats()

    return render_template("pages/srs/add_card.html", title="Add New Card", categories=categories, stats=stats)


@srs_bp.route("/categories/create", methods=["POST"])
@login_required
def create_category():
    """Create a new category (deck) and return to the form."""
    name = request.form.get("name")
    color = request.form.get("color", "#0d6efd")

    if not name:
        flash("Category name is required", "error")
        return redirect(url_for("srs_bp.add_card"))

    category = srs_service.create_category(name, color)
    flash(f"Category '{name}' created successfully", "success")

    return redirect(url_for("srs_bp.add_card"))
