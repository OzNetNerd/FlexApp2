# app/services/crisp/analytics.py
from app.models import Crisp, Relationship, db
from app.services.service_base import ServiceBase


class CrispAnalyticsService(ServiceBase):
    def get_recent_scores(self, limit=10):
        recent_scores = db.session.query(Crisp).order_by(Crisp.created_at.desc()).limit(limit).all()

        for score in recent_scores:
            relationship = Relationship.query.get(score.relationship_id)
            score.relationship_display_name = self.get_relationship_display_name(relationship)

        return recent_scores

    def get_score_statistics(self):
        all_scores = Crisp.query.all()
        total_assessments = len(all_scores)

        if total_assessments > 0:
            avg_credibility = sum(score.credibility for score in all_scores) / total_assessments
            avg_reliability = sum(score.reliability for score in all_scores) / total_assessments
            avg_intimacy = sum(score.intimacy for score in all_scores) / total_assessments
            avg_self_orientation = sum(score.self_orientation for score in all_scores) / total_assessments
            avg_score = sum(score.total_score for score in all_scores) / total_assessments
        else:
            avg_credibility = avg_reliability = avg_intimacy = avg_self_orientation = avg_score = 0

        high_trust_count = sum(1 for score in all_scores if score.total_score >= 3)
        low_trust_count = sum(1 for score in all_scores if score.total_score < 2)

        score_distribution = [
            sum(1 for score in all_scores if score.total_score < 1),
            sum(1 for score in all_scores if 1 <= score.total_score < 2),
            sum(1 for score in all_scores if 2 <= score.total_score < 3),
            sum(1 for score in all_scores if 3 <= score.total_score < 4),
            sum(1 for score in all_scores if score.total_score >= 4),
        ]

        return {
            "avg_credibility": avg_credibility,
            "avg_reliability": avg_reliability,
            "avg_intimacy": avg_intimacy,
            "avg_self_orientation": avg_self_orientation,
            "avg_score": avg_score,
            "high_trust_count": high_trust_count,
            "low_trust_count": low_trust_count,
            "total_assessments": total_assessments,
            "score_distribution": score_distribution
        }

    def get_relationship_display_name(self, relationship):
        if not relationship:
            return "Unknown Relationship"

        entity1_type = relationship.entity1_type
        entity2_type = relationship.entity2_type
        return f"{entity1_type.capitalize()} {relationship.entity1_id} - {entity2_type.capitalize()} {relationship.entity2_id}"