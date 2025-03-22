from flask import Blueprint, request, redirect, flash, url_for
from flask_login import login_required
from models import db, CRISPScore, Relationship

crisp_scores_bp = Blueprint("crisp_scores", __name__)

@crisp_scores_bp.route("/crisp_scores/<int:relationship_id>", methods=["POST"])
@login_required
def submit(relationship_id):
    relationship = Relationship.query.get_or_404(relationship_id)

    try:
        score = CRISPScore(
            relationship_id=relationship.id,
            credibility=int(request.form['credibility']),
            reliability=int(request.form['reliability']),
            intimacy=int(request.form['intimacy']),
            self_orientation=int(request.form['self_orientation'])
        )
        db.session.add(score)
        db.session.commit()
        flash("CRISP score submitted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error submitting CRISP score: {str(e)}", "danger")

    return redirect(url_for("contacts.view", item_id=relationship.contact_id))
