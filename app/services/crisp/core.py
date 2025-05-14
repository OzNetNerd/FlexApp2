# app/services/crisp/core.py
from app.models import Crisp, Relationship, db
from app.services.service_base import ServiceBase

class CrispService(ServiceBase):
    def get_relationship_display_name(self, relationship):
        if not relationship:
            return "Unknown Relationship"

        entity1_type = relationship.entity1_type
        entity2_type = relationship.entity2_type
        return f"{entity1_type.capitalize()} {relationship.entity1_id} - {entity2_type.capitalize()} {relationship.entity2_id}"

    def create_score(self, form_data):
        try:
            relationship_id = int(form_data["relationship_id"])
            relationship = Relationship.query.get_or_404(relationship_id)

            score = Crisp(
                relationship_id=relationship.id,
                credibility=int(form_data["credibility"]),
                reliability=int(form_data["reliability"]),
                intimacy=int(form_data["intimacy"]),
                self_orientation=int(form_data["self_orientation"]),
                notes=form_data.get("notes", ""),
            )
            db.session.add(score)
            db.session.commit()
            return True, "CRISP score submitted successfully."
        except Exception as e:
            db.session.rollback()
            return False, f"Error submitting CRISP score: {str(e)}"