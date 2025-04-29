from flask import render_template, request, redirect, url_for
from app.models.pages.srs import SRSItem
from app.routes.web.blueprint_factory import create_crud_blueprint
from app.services.srs_service import SRSService

# Create the service instance
srs_service = SRSService()

# Create the blueprint first
srs_items_bp = create_crud_blueprint(SRSItem, service=srs_service)


# Then add only the review route
@srs_items_bp.route("/<int:item_id>/review", methods=["GET", "POST"])
def review_item(item_id):
    """Web route for reviewing an SRS item."""
    item = srs_service.get_by_id(item_id)

    if request.method == "POST":
        rating = int(request.form.get("rating", 0))
        item = srs_service.schedule_review(item_id, rating)
        return redirect(url_for('srs_items_bp.index'))

    # Get navigation variables
    next_item_id = srs_service.get_next_due_item_id(item_id)
    prev_item_id = srs_service.get_prev_item_id(item_id)

    # Get stats if available
    try:
        stats = srs_service.get_stats()
    except:
        stats = None

    return render_template("pages/srs/view.html",
                           entity=item,
                           entity_id=item_id,
                           title=f"Review SRSItem",
                           next_item_id=next_item_id,
                           prev_item_id=prev_item_id,
                           stats=stats)