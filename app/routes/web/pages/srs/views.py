"""
SRS view classes for handling web routes.

This module contains view classes that implement the logic for SRS-related routes
in the web application. Each view class corresponds to a specific functionality
and handles HTTP methods appropriately.
"""

from flask import request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json

from app.routes.web.views.base_view import BaseView
from app.routes.web.utils.template_renderer import render_safely, RenderSafelyConfig
from app.routes.web.pages.srs.contexts import (
    SRSCardListContext, SRSCategoryContext, SRSFilteredCardsContext,
    SRSFilteredContext, SRSAddCardContext, SRSReviewContext
)
from app.utils.app_logging import get_logger, log_message_and_variables
from app.services.srs.constants import DEFAULT_EASE_FACTOR
from app.models.pages.srs import SRS
from app.routes.base_context import BaseContext

logger = get_logger()


class SRSReviewView(BaseView):
    """View class for reviewing SRS cards."""

    @login_required
    def get(self, item_id):
        """Handle GET request for reviewing an SRS item.

        Args:
            item_id (int): The ID of the card to review

        Returns:
            HTML for the review page
        """
        logger.info(f"User {current_user.id} reviewing SRS item {item_id}")
        item = self.service.get_by_id(item_id)
        is_batch = "batch" in request.args

        if not item:
            logger.warning(f"Card {item_id} not found during review attempt")
            flash("Card not found", "error")
            return redirect(url_for("srs_bp.dashboard"))

        # Get navigation variables
        logger.info("Preparing review navigation variables")
        next_item_id = self.service.get_next_due_item_id(item_id)
        prev_item_id = self.service.get_prev_item_id(item_id)

        # Get remaining batch items count if this is a batch review
        remaining_count = len(session.get("review_queue", [])) + 1 if is_batch else 0

        logger.info(f"Rendering review page for card {item_id}")

        context = SRSReviewContext(
            card=item, next_item_id=next_item_id, prev_item_id=prev_item_id,
            is_batch=is_batch, remaining_count=remaining_count
        )

        config = RenderSafelyConfig(
            template_path=self.template_path,
            context=context,
            error_message="Failed to render review page",
            endpoint_name=request.endpoint,
        )

        return render_safely(config)

    @login_required
    def post(self, item_id):
        """Handle POST request for submitting a review.

        Args:
            item_id (int): The ID of the card being reviewed

        Returns:
            Redirect to the next card or dashboard
        """
        logger.info(f"Processing review submission for card {item_id}")
        item = self.service.get_by_id(item_id)
        is_batch = "batch" in request.args

        if not item:
            logger.warning(f"Card {item_id} not found during review attempt")
            flash("Card not found", "error")
            return redirect(url_for("srs_bp.dashboard"))

        rating = int(request.form.get("rating", 0))
        logger.info(f"Card {item_id} received rating: {rating}")
        item = self.service.schedule_review(item_id, rating)

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
        next_due = self.service.get_next_due_item_id(item_id)
        if next_due:
            logger.info(f"Moving to next due card: {next_due}")
            return redirect(url_for("srs_bp.review_item", item_id=next_due))
        else:
            logger.info("No more due cards, returning to dashboard")
            return redirect(url_for("srs_bp.dashboard"))


class SRSBatchActionView(BaseView):
    """View class for batch operations on SRS cards."""

    @login_required
    def post(self):
        """Handle POST request for batch actions.

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
                card = self.service.get_by_id(int(card_id))
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
                    self.service.update(card, update_data)
            flash(f"Reset progress for {len(selected_ids)} cards", "success")
        elif action == "delete":
            # Delete selected cards
            logger.info(f"Deleting {len(selected_ids)} cards")
            count = 0
            for card_id in selected_ids:
                card = self.service.get_by_id(int(card_id))
                if card:
                    logger.info(f"Deleting card {card_id}")
                    card.delete()
                    count += 1
            flash(f"Deleted {count} cards", "success")
            logger.info(f"Successfully deleted {count} cards")

        # Redirect back to previous page
        return redirect(request.referrer or url_for("srs_bp.dashboard"))


class SRSAddCardView(BaseView):
    """View class for adding new SRS cards and categories."""

    @login_required
    def get(self):
        """Handle GET request for the add card form.

        Returns:
            HTML form for adding a card
        """
        logger.info(f"User {current_user.id} accessing add card form")

        # Get categories (decks) for dropdown
        logger.info("Retrieving categories for dropdown")
        categories = self.service.get_categories()

        # Get stats for footer
        logger.info("Retrieving stats for form footer")
        stats = self.service.get_stats()

        logger.info("Rendering add card form")

        context = SRSAddCardContext(categories=categories, stats=stats)

        config = RenderSafelyConfig(
            template_path=self.template_path,
            context=context,
            error_message="Failed to render add card form",
            endpoint_name=request.endpoint,
        )

        return render_safely(config)

    @login_required
    def post(self):
        """Handle POST request for adding a new card.

        Returns:
            Redirect to dashboard or add another card form
        """
        if request.endpoint == "srs_bp.create_category":
            return self._create_category()
        else:
            return self._add_card()

    def _add_card(self):
        """Process form submission to add a new card.

        Returns:
            Redirect to dashboard or add another card form
        """
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
            new_card["next_review_at"] = datetime.now(ZoneInfo("UTC")).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(
                days=1
            )

        # Save the card
        card = self.service.create(new_card)
        logger.info(f"Card created successfully with ID {card.id}")

        flash("Card added successfully", "success")

        # Handle different save actions
        if action == "save_add_another":
            logger.info("Redirecting to add another card")
            return redirect(url_for("srs_bp.add_card"))
        else:
            logger.info("Redirecting to dashboard after card creation")
            return redirect(url_for("srs_bp.dashboard"))

    def _create_category(self):
        """Process form submission to create a new category.

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

        category = self.service.create_category(name, color)
        logger.info(f"Category '{name}' created successfully with ID {category.id}")
        flash(f"Category '{name}' created successfully", "success")

        return redirect(url_for("srs_bp.add_card"))


class SRSCategoryView(BaseView):
    """View class for category-specific card views."""

    @login_required
    def get(self, category_type):
        """Handle GET request for viewing cards by category.

        Args:
            category_type (str): The type of category to filter by

        Returns:
            HTML for the category view
        """
        logger.info(f"User {current_user.id} viewing cards in category: {category_type}")
        cards = self.service.get_by_type(category_type)
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
            template_path=self.template_path,
            context=context,
            error_message=f"Failed to render category view for {category_type}",
            endpoint_name=request.endpoint,
        )

        return render_safely(config)


class SRSLearningStageView(BaseView):
    """View class for filtering cards by learning stage."""

    @login_required
    def get(self, stage):
        """Handle GET request for filtering cards by learning stage.

        Args:
            stage (str): The learning stage to filter by

        Returns:
            HTML for the filtered cards view
        """
        logger.info(f"User {current_user.id} filtering cards by learning stage: {stage}")
        valid_stages = ["new", "learning", "reviewing", "mastered"]
        if stage not in valid_stages:
            logger.warning(f"Invalid learning stage requested: {stage}")
            flash(f"Invalid learning stage: {stage}", "error")
            return redirect(url_for("srs_bp.dashboard"))

        cards = self.service.get_cards_by_learning_stage(stage)
        logger.info(f"Retrieved {len(cards)} cards in learning stage {stage}")

        stage_names = {
            "new": "New Cards",
            "learning": "Learning Cards",
            "reviewing": "Review Cards",
            "mastered": "Mastered Cards"
        }

        logger.info(f"Rendering filtered cards for learning stage: {stage_names[stage]}")

        context = SRSFilteredCardsContext(
            cards=cards,
            title=stage_names[stage],
            filters={"learning_stage": stage},
            category_counts=self.service.count_by_type(),
            due_category_counts=self.service.count_due_by_type(),
            due_today=self.service.count_due_today(),
            total_cards=self.service.count_total(),
            active_tab=stage,
        )

        config = RenderSafelyConfig(
            template_path=self.template_path,
            context=context,
            error_message=f"Failed to render cards by learning stage: {stage}",
            endpoint_name=request.endpoint,
        )

        return render_safely(config)


class SRSDifficultyView(BaseView):
    """View class for filtering cards by difficulty level."""

    @login_required
    def get(self, difficulty):
        """Handle GET request for filtering cards by difficulty.

        Args:
            difficulty (str): The difficulty level to filter by

        Returns:
            HTML for the filtered cards view
        """
        logger.info(f"User {current_user.id} filtering cards by difficulty: {difficulty}")
        valid_difficulties = ["hard", "medium", "easy"]
        if difficulty not in valid_difficulties:
            logger.warning(f"Invalid difficulty level requested: {difficulty}")
            flash(f"Invalid difficulty level: {difficulty}", "error")
            return redirect(url_for("srs_bp.dashboard"))

        cards = self.service.get_cards_by_difficulty(difficulty)
        logger.info(f"Retrieved {len(cards)} cards with difficulty {difficulty}")

        difficulty_names = {
            "hard": "Hard Cards",
            "medium": "Medium Difficulty Cards",
            "easy": "Easy Cards"
        }

        logger.info(f"Rendering filtered cards for difficulty: {difficulty_names[difficulty]}")

        context = SRSFilteredCardsContext(
            cards=cards,
            title=difficulty_names[difficulty],
            filters={"difficulty": difficulty},
            category_counts=self.service.count_by_type(),
            due_category_counts=self.service.count_due_by_type(),
            due_today=self.service.count_due_today(),
            total_cards=self.service.count_total(),
            active_tab=f"difficulty_{difficulty}",
        )

        config = RenderSafelyConfig(
            template_path=self.template_path,
            context=context,
            error_message=f"Failed to render cards by difficulty: {difficulty}",
            endpoint_name=request.endpoint,
        )

        return render_safely(config)


class SRSPerformanceView(BaseView):
    """View class for filtering cards by performance level."""

    @login_required
    def get(self, performance):
        """Handle GET request for filtering cards by performance.

        Args:
            performance (str): The performance level to filter by

        Returns:
            HTML for the filtered cards view
        """
        logger.info(f"User {current_user.id} filtering cards by performance: {performance}")
        valid_performances = ["struggling", "average", "strong"]
        if performance not in valid_performances:
            logger.warning(f"Invalid performance level requested: {performance}")
            flash(f"Invalid performance level: {performance}", "error")
            return redirect(url_for("srs_bp.dashboard"))

        cards = self.service.get_cards_by_performance(performance)
        logger.info(f"Retrieved {len(cards)} cards with performance {performance}")

        performance_names = {
            "struggling": "Struggling Cards",
            "average": "Average Performance Cards",
            "strong": "Strong Performance Cards"
        }

        logger.info(f"Rendering filtered cards for performance: {performance_names[performance]}")

        context = SRSFilteredCardsContext(
            cards=cards,
            title=performance_names[performance],
            filters={"performance": performance},
            category_counts=self.service.count_by_type(),
            due_category_counts=self.service.count_due_by_type(),
            due_today=self.service.count_due_today(),
            total_cards=self.service.count_total(),
            active_tab=f"performance_{performance}",
        )

        config = RenderSafelyConfig(
            template_path=self.template_path,
            context=context,
            error_message=f"Failed to render cards by performance: {performance}",
            endpoint_name=request.endpoint,
        )

        return render_safely(config)


class SRSReviewStrategyView(BaseView):
    """View class for review strategies and batch review."""

    @login_required
    def get(self, strategy=None):
        """Handle GET request for review strategy or batch review.

        Args:
            strategy (str, optional): The review strategy to use

        Returns:
            Redirect to the first card in the batch review
        """
        if request.endpoint == "srs_bp.review_batch":
            return self._review_batch()
        else:
            return self._review_by_strategy(strategy)

    def _review_by_strategy(self, strategy):
        """Start a review session using a specific review strategy.

        Args:
            strategy (str): The review strategy to use

        Returns:
            Redirect to the first card in the batch review
        """
        logger.info(f"User {current_user.id} starting review with strategy: {strategy}")
        valid_strategies = ["due_mix", "priority_first", "hard_cards_first",
                           "mastery_boost", "struggling_focus", "new_mix"]
        if strategy not in valid_strategies:
            logger.warning(f"Invalid review strategy requested: {strategy}")
            flash(f"Invalid review strategy: {strategy}", "error")
            return redirect(url_for("srs_bp.dashboard"))

        # Get cards based on strategy
        cards = self.service.get_review_strategy(strategy, limit=20)
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

    def _review_batch(self):
        """Review a batch of selected cards.

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


# Add this to app/routes/web/pages/srs/views.py

class SRSItemView(BaseView):
    """View class for individual SRS items."""

    @login_required
    def get(self, entity_id):
        """Handle GET request for viewing an SRS item."""
        logger.info(f"User {current_user.id} viewing SRS item {entity_id}")
        item = self.service.get_by_id(entity_id)

        if not item:
            logger.warning(f"SRS item {entity_id} not found")
            flash("SRS item not found", "error")
            return redirect(url_for("srs_bp.dashboard"))

        # Create a form instance for displaying the data
        from app.forms.srs import SRSForm
        form = SRSForm(obj=item)

        # Create a proper BaseContext object
        context = BaseContext(
            entity_table_name="SRS Card",
            entity_name=item.question[:30] + "..." if len(item.question) > 30 else item.question,
            entity_base_route="srs_bp",
            model_name="SRS",
            id=entity_id,
            form=form,
            action="view",
            submit_url=url_for("srs_bp.edit", entity_id=entity_id)
        )

        config = RenderSafelyConfig(
            template_path="layouts/crud_form.html",
            context=context,
            error_message="Failed to render SRS item view",
            endpoint_name=request.endpoint,
        )

        return render_safely(config)