from flask import Blueprint, request, redirect, flash, url_for
from flask_login import login_required
from app.models import db, CRISPScore, Relationship

from app.utils.app_logging import get_logger
logger = get_logger()

# Define blueprint with explicit prefix
crisp_scores_bp = Blueprint("crisp_scores_bp", __name__, url_prefix="/crisp_scores")


@crisp_scores_bp.route("/<int:relationship_id>", methods=["POST"])
@login_required
def submit(relationship_id):
    """Submit a CRISP score for a relationship."""
    relationship = Relationship.query.get_or_404(relationship_id)

    try:
        score = CRISPScore(
            relationship_id=relationship.id,
            credibility=int(request.form["credibility"]),
            reliability=int(request.form["reliability"]),
            intimacy=int(request.form["intimacy"]),
            self_orientation=int(request.form["self_orientation"]),
        )
        db.session.add(score)
        db.session.commit()
        flash("CRISP score submitted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error submitting CRISP score: {str(e)}", "danger")

    return redirect(url_for("contacts.view", entity_id=relationship.contact_id))


logger.info("Successfully set up ' CRISP Score' routes.")
