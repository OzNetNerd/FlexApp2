from flask import render_template
from app.routes.web.views.base_view import DashboardView, RecordsView
from app.models import Crisp, Relationship


class CrispDashboardView(DashboardView):
    def get(self):
        stats = self.service.get_score_statistics()
        recent_scores = self.service.get_recent_scores()

        return render_template(
            self.template_path,
            avg_credibility=stats["avg_credibility"],
            avg_reliability=stats["avg_reliability"],
            avg_intimacy=stats["avg_intimacy"],
            avg_self_orientation=stats["avg_self_orientation"],
            avg_score=stats["avg_score"],
            high_trust_count=stats["high_trust_count"],
            low_trust_count=stats["low_trust_count"],
            total_assessments=stats["total_assessments"],
            score_distribution=stats["score_distribution"],
            recent_scores=recent_scores,
        )


class CrispScoresView(RecordsView):
    def get(self):
        scores = Crisp.query.order_by(Crisp.created_at.desc()).all()

        for score in scores:
            relationship = Relationship.query.get(score.relationship_id)
            score.relationship_display_name = self.service.get_relationship_display_name(relationship)

        return render_template(self.template_path, scores=scores)


class CrispDetailView(RecordsView):
    def get(self, score_id):
        score = Crisp.query.get_or_404(score_id)
        relationship = Relationship.query.get(score.relationship_id)
        score.relationship_display_name = self.service.get_relationship_display_name(relationship)

        historical_scores = Crisp.query.filter_by(relationship_id=score.relationship_id).order_by(
            Crisp.created_at).all()
        historical_dates = [score.created_at.strftime("%Y-%m-%d") for score in historical_scores]
        historical_scores_data = [float(score.total_score) for score in historical_scores]
        historical_credibility = [score.credibility for score in historical_scores]
        historical_reliability = [score.reliability for score in historical_scores]
        historical_intimacy = [score.intimacy for score in historical_scores]
        historical_self_orientation = [score.self_orientation for score in historical_scores]

        return render_template(
            self.template_path,
            score=score,
            historical_dates=historical_dates,
            historical_scores=historical_scores_data,
            historical_credibility=historical_credibility,
            historical_reliability=historical_reliability,
            historical_intimacy=historical_intimacy,
            historical_self_orientation=historical_self_orientation,
        )


class CrispFormView(RecordsView):
    def get(self, score_id=None):
        score = None
        relationship = None

        if score_id:
            score = Crisp.query.get_or_404(score_id)
            relationship = Relationship.query.get(score.relationship_id)
            relationship.display_name = self.service.get_relationship_display_name(relationship)
        else:
            relationships = Relationship.query.all()
            for rel in relationships:
                rel.display_name = self.service.get_relationship_display_name(rel)

        return render_template(
            self.template_path,
            score=score,
            relationship=relationship,
            relationships=relationships if not score else None
        )


class CrispComparisonView(RecordsView):
    def get(self):
        all_relationships = Relationship.query.all()
        for relationship in all_relationships:
            relationship.display_name = self.service.get_relationship_display_name(relationship)

        selected_ids = self.request.args.getlist("relationship_ids", type=int)
        comparison_data = []
        comparison_labels = []
        comparison_scores = []
        component_datasets = []

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
                    latest_score = Crisp.query.filter_by(relationship_id=relationship_id).order_by(
                        Crisp.created_at.desc()).first()

                    if latest_score:
                        display_name = self.service.get_relationship_display_name(relationship)

                        comparison_data.append({
                            "display_name": display_name,
                            "credibility": latest_score.credibility,
                            "reliability": latest_score.reliability,
                            "intimacy": latest_score.intimacy,
                            "self_orientation": latest_score.self_orientation,
                            "total_score": latest_score.total_score,
                            "last_updated": latest_score.updated_at,
                            "score_id": latest_score.id,
                        })

                        comparison_labels.append(display_name)
                        comparison_scores.append(float(latest_score.total_score))

                        color = colors[i % len(colors)]
                        component_datasets.append({
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
                        })

        return render_template(
            self.template_path,
            all_relationships=all_relationships,
            selected_relationships=selected_ids,
            comparison_data=comparison_data,
            comparison_labels=comparison_labels,
            comparison_scores=comparison_scores,
            component_datasets=component_datasets,
        )