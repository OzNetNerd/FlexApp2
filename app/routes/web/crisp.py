from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.models import CRISPScore, Relationship, db
from app.utils.app_logging import get_logger
from datetime import datetime, timedelta
import json

logger = get_logger()

# Define blueprint with explicit prefix
crisp_scores_bp = Blueprint("crisp_scores_bp", __name__, url_prefix="/crisp")


@crisp_scores_bp.route("/dashboard")
@login_required
def dashboard():
    """CRISP Score Dashboard with metrics and visualizations."""
    # Get basic statistics
    all_scores = CRISPScore.query.all()
    total_assessments = len(all_scores)

    # Calculate averages
    if total_assessments > 0:
        avg_credibility = sum(score.credibility for score in all_scores) / total_assessments
        avg_reliability = sum(score.reliability for score in all_scores) / total_assessments
        avg_intimacy = sum(score.intimacy for score in all_scores) / total_assessments
        avg_self_orientation = sum(score.self_orientation for score in all_scores) / total_assessments
        avg_score = sum(score.total_score for score in all_scores) / total_assessments
    else:
        avg_credibility = avg_reliability = avg_intimacy = avg_self_orientation = avg_score = 0

    # Count high and low trust relationships
    high_trust_count = sum(1 for score in all_scores if score.total_score >= 3)
    low_trust_count = sum(1 for score in all_scores if score.total_score < 2)

    # Score distribution for chart
    score_distribution = [
        sum(1 for score in all_scores if score.total_score < 1),  # Very Low
        sum(1 for score in all_scores if 1 <= score.total_score < 2),  # Low
        sum(1 for score in all_scores if 2 <= score.total_score < 3),  # Moderate
        sum(1 for score in all_scores if 3 <= score.total_score < 4),  # Good
        sum(1 for score in all_scores if score.total_score >= 4),  # Excellent
    ]

    # Get recent scores
    recent_scores = db.session.query(CRISPScore).order_by(CRISPScore.created_at.desc()).limit(10).all()

    # Prepare relationship display names
    for score in recent_scores:
        relationship = Relationship.query.get(score.relationship_id)
        if relationship:
            entity1_type = relationship.entity1_type
            entity2_type = relationship.entity2_type
            score.relationship_display_name = (
                f"{entity1_type.capitalize()} {relationship.entity1_id} - {entity2_type.capitalize()} {relationship.entity2_id}"
            )

    return render_template(
        "pages/crisp/dashboard.html",
        avg_credibility=avg_credibility,
        avg_reliability=avg_reliability,
        avg_intimacy=avg_intimacy,
        avg_self_orientation=avg_self_orientation,
        avg_score=avg_score,
        high_trust_count=high_trust_count,
        low_trust_count=low_trust_count,
        total_assessments=total_assessments,
        score_distribution=score_distribution,
        recent_scores=recent_scores,
    )


@crisp_scores_bp.route("/scores")
@login_required
def list_scores():
    """List all CRISP scores with filtering options."""
    # Get all scores with their relationships
    scores = CRISPScore.query.order_by(CRISPScore.created_at.desc()).all()

    # Prepare relationship display names
    for score in scores:
        relationship = Relationship.query.get(score.relationship_id)
        if relationship:
            entity1_type = relationship.entity1_type
            entity2_type = relationship.entity2_type
            score.relationship_display_name = (
                f"{entity1_type.capitalize()} {relationship.entity1_id} - {entity2_type.capitalize()} {relationship.entity2_id}"
            )

    return render_template("pages/crisp/list.html", scores=scores)


@crisp_scores_bp.route("/score/<int:score_id>")
@login_required
def view_score(score_id):
    """View the details of a specific CRISP score."""
    score = CRISPScore.query.get_or_404(score_id)
    relationship = Relationship.query.get(score.relationship_id)

    # Prepare relationship display name
    entity1_type = relationship.entity1_type
    entity2_type = relationship.entity2_type
    score.relationship_display_name = (
        f"{entity1_type.capitalize()} {relationship.entity1_id} - {entity2_type.capitalize()} {relationship.entity2_id}"
    )

    # Get historical scores for this relationship
    historical_scores = CRISPScore.query.filter_by(relationship_id=score.relationship_id).order_by(CRISPScore.created_at).all()

    # Prepare data for historical chart
    historical_dates = [score.created_at.strftime("%Y-%m-%d") for score in historical_scores]
    historical_scores_data = [float(score.total_score) for score in historical_scores]
    historical_credibility = [score.credibility for score in historical_scores]
    historical_reliability = [score.reliability for score in historical_scores]
    historical_intimacy = [score.intimacy for score in historical_scores]
    historical_self_orientation = [score.self_orientation for score in historical_scores]

    return render_template(
        "pages/crisp/details.html",
        score=score,
        historical_dates=historical_dates,
        historical_scores=historical_scores_data,
        historical_credibility=historical_credibility,
        historical_reliability=historical_reliability,
        historical_intimacy=historical_intimacy,
        historical_self_orientation=historical_self_orientation,
    )


@crisp_scores_bp.route("/create")
@login_required
def create_score():
    """Form to create a new CRISP score."""
    # Get all relationships
    relationships = Relationship.query.all()

    # Prepare relationship display names
    for relationship in relationships:
        entity1_type = relationship.entity1_type
        entity2_type = relationship.entity2_type
        relationship.display_name = (
            f"{entity1_type.capitalize()} {relationship.entity1_id} - {entity2_type.capitalize()} {relationship.entity2_id}"
        )

    return render_template("pages/crisp/form.html", relationships=relationships, score=None, relationship=None)


@crisp_scores_bp.route("/edit/<int:score_id>")
@login_required
def edit_score(score_id):
    """Form to edit an existing CRISP score."""
    score = CRISPScore.query.get_or_404(score_id)
    relationship = Relationship.query.get(score.relationship_id)

    # Prepare relationship display name
    entity1_type = relationship.entity1_type
    entity2_type = relationship.entity2_type
    relationship.display_name = (
        f"{entity1_type.capitalize()} {relationship.entity1_id} - {entity2_type.capitalize()} {relationship.entity2_id}"
    )

    return render_template("pages/crisp/form.html", score=score, relationship=relationship)


@crisp_scores_bp.route("/score/<int:relationship_id>", methods=["POST"])
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
            notes=request.form.get("notes", ""),
        )
        db.session.add(score)
        db.session.commit()
        flash("CRISP score submitted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error submitting CRISP score: {str(e)}", "danger")

    return redirect(url_for("crisp_scores_bp.dashboard"))


@crisp_scores_bp.route("/submit-new", methods=["POST"])
@login_required
def submit_new():
    """Submit a CRISP score for a newly selected relationship."""
    try:
        relationship_id = int(request.form["relationship_id"])
        relationship = Relationship.query.get_or_404(relationship_id)

        score = CRISPScore(
            relationship_id=relationship.id,
            credibility=int(request.form["credibility"]),
            reliability=int(request.form["reliability"]),
            intimacy=int(request.form["intimacy"]),
            self_orientation=int(request.form["self_orientation"]),
            notes=request.form.get("notes", ""),
        )
        db.session.add(score)
        db.session.commit()
        flash("CRISP score submitted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error submitting CRISP score: {str(e)}", "danger")

    return redirect(url_for("crisp_scores_bp.dashboard"))


@crisp_scores_bp.route("/comparison")
@login_required
def comparison():
    """Compare CRISP scores across multiple relationships."""
    # Get all relationships
    all_relationships = Relationship.query.all()

    # Prepare relationship display names
    for relationship in all_relationships:
        entity1_type = relationship.entity1_type
        entity2_type = relationship.entity2_type
        relationship.display_name = (
            f"{entity1_type.capitalize()} {relationship.entity1_id} - {entity2_type.capitalize()} {relationship.entity2_id}"
        )

    # Get selected relationships from query parameters
    selected_ids = request.args.getlist("relationship_ids", type=int)

    comparison_data = []
    comparison_labels = []
    comparison_scores = []
    component_datasets = []

    # Prepare comparison data if relationships are selected
    if selected_ids:
        colors = [
            {"border": "rgba(0, 123, 255, 1)", "background": "rgba(0, 123, 255, 0.2)"},
            {"border": "rgba(40, 167, 69, 1)", "background": "rgba(40, 167, 69, 0.2)"},
            {"border": "rgba(23, 162, 184, 1)", "background": "rgba(23, 162, 184, 0.2)"},
            {"border": "rgba(255, 193, 7, 1)", "background": "rgba(255, 193, 7, 0.2)"},
            {"border": "rgba(220, 53, 69, 1)", "background": "rgba(220, 53, 69, 0.2)"},
        ]

        for i, relationship_id in enumerate(selected_ids):
            relationship = Relationship.query.get(relationship_id)
            if relationship:
                # Get the most recent CRISP score for this relationship
                latest_score = CRISPScore.query.filter_by(relationship_id=relationship_id).order_by(CRISPScore.created_at.desc()).first()

                if latest_score:
                    # Prepare display data
                    entity1_type = relationship.entity1_type
                    entity2_type = relationship.entity2_type
                    display_name = (
                        f"{entity1_type.capitalize()} {relationship.entity1_id} - {entity2_type.capitalize()} {relationship.entity2_id}"
                    )

                    comparison_data.append(
                        {
                            "display_name": display_name,
                            "credibility": latest_score.credibility,
                            "reliability": latest_score.reliability,
                            "intimacy": latest_score.intimacy,
                            "self_orientation": latest_score.self_orientation,
                            "total_score": latest_score.total_score,
                            "last_updated": latest_score.updated_at,
                            "score_id": latest_score.id,
                        }
                    )

                    comparison_labels.append(display_name)
                    comparison_scores.append(float(latest_score.total_score))

                    # Prepare radar chart dataset
                    color = colors[i % len(colors)]
                    component_datasets.append(
                        {
                            "label": display_name,
                            "data": [
                                latest_score.credibility,
                                latest_score.reliability,
                                latest_score.intimacy,
                                latest_score.self_orientation,
                            ],
                            "backgroundColor": color["background"],
                            "borderColor": color["border"],
                            "pointBackgroundColor": color["border"],
                            "pointBorderColor": "#fff",
                            "pointHoverBackgroundColor": "#fff",
                            "pointHoverBorderColor": color["border"],
                        }
                    )

    return render_template(
        "pages/crisp/comparison.html",
        all_relationships=all_relationships,
        selected_relationships=selected_ids,
        comparison_data=comparison_data,
        comparison_labels=comparison_labels,
        comparison_scores=comparison_scores,
        component_datasets=component_datasets,
    )


logger.info("Successfully set up CRISP Score routes.")
