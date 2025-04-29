from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, UTC
from app.models.pages.srs import SRS, ReviewHistory
from app.services.srs_service import SRSService
from app.routes.web.blueprint_factory import create_crud_blueprint

# Create the service instance
srs_service = SRSService()

# Create a blueprint with CRUD operations
srs_bp = create_crud_blueprint(SRS, service=srs_service)


# Dashboard route
@srs_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """Render the flashcard dashboard."""
    # Get summary statistics
    stats = {
        'total_cards': srs_service.count_total(),
        'due_today': srs_service.count_due_today(),
        'success_rate': srs_service.calculate_success_rate(),
        'days_streak': srs_service.get_streak_days(),
        'weekly_reviews': srs_service.count_weekly_reviews(),
        'mastered_cards': srs_service.count_mastered_cards_this_month(),
        'retention_increase': srs_service.calculate_retention_increase(),
        'perfect_reviews': srs_service.count_consecutive_perfect_reviews()
    }

    # Get card categories with counts
    categories = [
        {
            'name': 'Companies',
            'type': 'company',
            'icon': 'building',
            'color': 'primary',
            'total': srs_service.count_by_type('company'),
            'due': srs_service.count_due_by_type('company'),
            'progress': srs_service.calculate_progress_by_type('company')
        },
        {
            'name': 'Contacts',
            'type': 'contact',
            'icon': 'people',
            'color': 'success',
            'total': srs_service.count_by_type('contact'),
            'due': srs_service.count_due_by_type('contact'),
            'progress': srs_service.calculate_progress_by_type('contact')
        },
        {
            'name': 'Opportunities',
            'type': 'opportunity',
            'icon': 'graph-up-arrow',
            'color': 'danger',
            'total': srs_service.count_by_type('opportunity'),
            'due': srs_service.count_due_by_type('opportunity'),
            'progress': srs_service.calculate_progress_by_type('opportunity')
        }
    ]

    # Get due cards for today (limited to 5 for display)
    due_cards = srs_service.get_due_cards(limit=5)

    # Get learning progress data for chart
    progress_data = srs_service.get_learning_progress_data(months=7)

    return render_template(
        "pages/srs/dashboard.html",
        stats=stats,
        categories=categories,
        due_cards=due_cards,
        progress_data=progress_data
    )


# Due cards route
@srs_bp.route("/due", methods=["GET"])
@login_required
def due_cards():
    """View all cards due for review today."""
    cards = srs_service.get_due_cards()
    return render_template(
        "pages/srs/due.html",
        cards=cards,
        title="Cards Due Today"
    )


# Review card route
@srs_bp.route("/<int:item_id>/review", methods=["GET", "POST"])
@login_required
def review_item(item_id):
    """Web route for reviewing an SRS item."""
    item = srs_service.get_by_id(item_id)

    if not item:
        flash("Card not found", "error")
        return redirect(url_for('srs_bp.dashboard'))

    if request.method == "POST":
        rating = int(request.form.get("rating", 0))
        item = srs_service.schedule_review(item_id, rating)

        # Record review history
        history = ReviewHistory(
            srs_item_id=item_id,
            rating=rating,
            interval=item.interval,
            ease_factor=item.ease_factor
        )
        history.save()

        flash("Card reviewed successfully", "success")

        # If there are more due cards, go to the next one
        next_due = srs_service.get_next_due_item_id(item_id)
        if next_due:
            return redirect(url_for('srs_bp.review_item', item_id=next_due))
        else:
            return redirect(url_for('srs_bp.dashboard'))

    # Get navigation variables
    next_item_id = srs_service.get_next_due_item_id(item_id)
    prev_item_id = srs_service.get_prev_item_id(item_id)

    return render_template(
        "pages/srs/review.html",
        card=item,
        title="Review Card",
        next_item_id=next_item_id,
        prev_item_id=prev_item_id
    )


# Category view route
@srs_bp.route("/category/<string:category_type>", methods=["GET"])
@login_required
def category_view(category_type):
    """View cards by category."""
    cards = srs_service.get_by_type(category_type)

    category_info = {
        'company': {'name': 'Companies', 'color': 'primary'},
        'contact': {'name': 'Contacts', 'color': 'success'},
        'opportunity': {'name': 'Opportunities', 'color': 'danger'}
    }

    info = category_info.get(category_type, {'name': 'Unknown', 'color': 'secondary'})

    return render_template(
        "pages/srs/category.html",
        cards=cards,
        category_type=category_type,
        category_name=info['name'],
        category_color=info['color'],
        title=f"{info['name']} Cards"
    )


# Statistics route
@srs_bp.route("/stats", methods=["GET"])
@login_required
def statistics():
    """View detailed learning statistics."""
    stats = srs_service.get_detailed_stats()
    return render_template(
        "pages/srs/stats.html",
        stats=stats,
        title="Learning Statistics"
    )


# API endpoint for chart data
@srs_bp.route("/api/progress-data", methods=["GET"])
@login_required
def progress_data():
    """Get progress data for charts."""
    months = request.args.get('months', 7, type=int)
    data = srs_service.get_learning_progress_data(months=months)
    return jsonify(data)


# Register the blueprint
def register_srs_blueprint(app):
    """Register the SRS blueprint with the app."""
    app.register_blueprint(srs_bp, url_prefix='/flashcards')


@srs_bp.route("/learning-stage/<stage>", methods=["GET"])
@login_required
def cards_by_learning_stage(stage):
    """View cards by learning stage."""
    valid_stages = ['new', 'learning', 'reviewing', 'mastered']
    if stage not in valid_stages:
        flash(f"Invalid learning stage: {stage}", "error")
        return redirect(url_for('srs_bp.dashboard'))

    cards = srs_service.get_cards_by_learning_stage(stage)

    stage_names = {
        'new': 'New Cards',
        'learning': 'Learning Cards',
        'reviewing': 'Review Cards',
        'mastered': 'Mastered Cards'
    }

    return render_template(
        "pages/srs/filtered_cards.html",
        cards=cards,
        title=stage_names[stage],
        filters={'learning_stage': stage},
        category_counts=srs_service.count_by_type(),
        due_category_counts=srs_service.count_due_by_type(),
        due_today=srs_service.count_due_today(),
        total_cards=srs_service.count_total(),
        active_tab=stage
    )


@srs_bp.route("/difficulty/<difficulty>", methods=["GET"])
@login_required
def cards_by_difficulty(difficulty):
    """View cards by difficulty level."""
    valid_difficulties = ['hard', 'medium', 'easy']
    if difficulty not in valid_difficulties:
        flash(f"Invalid difficulty level: {difficulty}", "error")
        return redirect(url_for('srs_bp.dashboard'))

    cards = srs_service.get_cards_by_difficulty(difficulty)

    difficulty_names = {
        'hard': 'Hard Cards',
        'medium': 'Medium Difficulty Cards',
        'easy': 'Easy Cards'
    }

    return render_template(
        "pages/srs/filtered_cards.html",
        cards=cards,
        title=difficulty_names[difficulty],
        filters={'difficulty': difficulty},
        category_counts=srs_service.count_by_type(),
        due_category_counts=srs_service.count_due_by_type(),
        due_today=srs_service.count_due_today(),
        total_cards=srs_service.count_total(),
        active_tab=f'difficulty_{difficulty}'
    )


@srs_bp.route("/performance/<performance>", methods=["GET"])
@login_required
def cards_by_performance(performance):
    """View cards by performance level."""
    valid_performances = ['struggling', 'average', 'strong']
    if performance not in valid_performances:
        flash(f"Invalid performance level: {performance}", "error")
        return redirect(url_for('srs_bp.dashboard'))

    cards = srs_service.get_cards_by_performance(performance)

    performance_names = {
        'struggling': 'Struggling Cards',
        'average': 'Average Performance Cards',
        'strong': 'Strong Performance Cards'
    }

    return render_template(
        "pages/srs/filtered_cards.html",
        cards=cards,
        title=performance_names[performance],
        filters={'performance': performance},
        category_counts=srs_service.count_by_type(),
        due_category_counts=srs_service.count_due_by_type(),
        due_today=srs_service.count_due_today(),
        total_cards=srs_service.count_total(),
        active_tab=f'performance_{performance}'
    )


@srs_bp.route("/strategy/<strategy>", methods=["GET"])
@login_required
def review_by_strategy(strategy):
    """Start a review session using a specific review strategy."""
    valid_strategies = ['due_mix', 'priority_first', 'hard_cards_first', 'mastery_boost', 'struggling_focus', 'new_mix']
    if strategy not in valid_strategies:
        flash(f"Invalid review strategy: {strategy}", "error")
        return redirect(url_for('srs_bp.dashboard'))

    # Get cards based on strategy
    cards = srs_service.get_review_strategy(strategy, limit=20)

    if not cards:
        flash("No cards available for this review strategy", "warning")
        return redirect(url_for('srs_bp.dashboard'))

    # Store card IDs in session for review
    session['review_queue'] = [card.id for card in cards]

    strategy_names = {
        'due_mix': 'Mixed Categories Review',
        'priority_first': 'Overdue First Review',
        'hard_cards_first': 'Difficult Cards Focus',
        'mastery_boost': 'Mastery Boost Review',
        'struggling_focus': 'Struggling Cards Focus',
        'new_mix': 'New & Due Cards Mix'
    }

    # Set session variable for strategy name to display during review
    session['review_strategy'] = strategy_names[strategy]

    # Redirect to first card in queue
    return redirect(url_for('srs_bp.review_item', item_id=cards[0].id, batch=True))