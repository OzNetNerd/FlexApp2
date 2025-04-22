# app/routes/api/srs.py

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import current_user
from app.routes.api.route_registration import (
    register_api_crud_routes,
    ApiCrudRouteConfig,
    json_response,
    ErrorAPIContext,
    ListAPIContext,
)
from app.services.srs_service import SRSService
from app.models.srs_item import SRSItem
from app.models.review_history import ReviewHistory

logger = logging.getLogger(__name__)

# Define entity names
ENTITY_NAME = "SRSItem"
ENTITY_PLURAL_NAME = "srs"

# Blueprint setup
srs_api_bp = Blueprint(
    f"{ENTITY_NAME.lower()}_api", __name__, url_prefix=f"/api/{ENTITY_PLURAL_NAME.lower()}"
)

# Service instance
srs_service = SRSService()

# Register standard CRUD index route
srs_api_crud_config = ApiCrudRouteConfig(
    blueprint=srs_api_bp,
    entity_table_name=ENTITY_NAME,
    service=srs_service,
)
register_api_crud_routes(srs_api_crud_config)


# Custom endpoints
@srs_api_bp.route("/due", methods=["GET"])
def get_due():
    try:
        items = srs_service.get_due_items()
        logger.info(f"Found {len(items)} due SRS items")
        return json_response(
            ListAPIContext(
                entity_table_name=ENTITY_NAME,
                items=items,
                total_count=len(items),
            )
        )
    except Exception as e:
        logger.error(f"Error fetching due SRS cards: {e}", exc_info=True)
        return json_response(
            ErrorAPIContext(message=str(e), status_code=500)
        )


@srs_api_bp.route("/<int:entity_id>/preview", methods=["GET"])
def preview_intervals(entity_id):
    """Get preview of intervals for each rating."""
    logger.info(f"Previewing intervals for SRSItem id={entity_id}")

    try:
        item = srs_service.get_by_id(entity_id)
        if not item:
            logger.warning(f"SRSItem with id={entity_id} not found")
            return jsonify({"error": "Item not found"}), 404

        # Create preview for each rating (0-5)
        intervals = {}
        for rating in range(6):
            # Calculate new interval without saving
            try:
                # If the service has a calculate_next_interval method
                new_ease, new_interval, _ = srs_service.calculate_next_interval(
                    item, rating, save=False
                )
            except AttributeError:
                # Fallback to using the FSRS algorithm directly if needed
                import fsrs
                new_ease, new_interval, _ = fsrs.srs1.step(
                    rating,
                    item.repetition,
                    item.interval,
                    item.ease_factor,
                )

            intervals[str(rating)] = new_interval

        logger.info(f"Interval previews for item {entity_id}: {intervals}")
        return jsonify(intervals)
    except Exception as e:
        logger.error(f"Error calculating interval previews: {e}", exc_info=True)
        return json_response(
            ErrorAPIContext(message=str(e), status_code=500)
        )


@srs_api_bp.route("/<int:entity_id>/review", methods=["POST"])
def submit_review(entity_id):
    try:
        data = request.get_json() or {}
        rating = int(data.get("rating", 0))
        answer_given = data.get("answer_given", "")

        logger.info(f"Reviewing SRSItem id={entity_id} with rating={rating}")

        updated = srs_service.schedule_review(entity_id, rating)

        # Save the answer given by the user if provided
        if answer_given and hasattr(updated, 'user_answer'):
            updated.user_answer = answer_given
            srs_service.update(updated)
            logger.info(f"Saved user answer for SRSItem id={entity_id}")

        logger.info(f"Successfully updated SRSItem id={entity_id}, next review at {updated.next_review_at}")

        return jsonify(updated.to_dict())
    except Exception as e:
        logger.error(f"Error scheduling review for item {entity_id}: {e}", exc_info=True)
        return json_response(
            ErrorAPIContext(message=str(e), status_code=500)
        )


@srs_api_bp.route("/stats", methods=["GET"])
def get_stats():
    """Get SRS statistics for the current user."""
    logger.info("Fetching SRS stats")

    try:
        total_cards = SRSItem.query.count()
        cards_due = SRSItem.query.filter(SRSItem.next_review_at <= datetime.utcnow()).count()

        today_start = datetime.today().replace(hour=0, minute=0, second=0)
        cards_reviewed_today = ReviewHistory.query.filter(
            ReviewHistory.created_at >= today_start
        ).count()

        stats = {
            "total_cards": total_cards,
            "cards_due": cards_due,
            "cards_reviewed_today": cards_reviewed_today
        }

        logger.info(f"SRS stats: {stats}")
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting SRS stats: {e}", exc_info=True)
        return json_response(
            ErrorAPIContext(message=str(e), status_code=500)
        )


logger.info(f"{ENTITY_PLURAL_NAME} API routes registered successfully.")