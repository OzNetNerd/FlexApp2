from app.models.base import BaseModel, db
from app.utils.app_logging import get_logger

logger = get_logger()


class CRISPScore(BaseModel):
    __tablename__ = "crisp_scores"

    # Add primary key
    id = db.Column(db.Integer, primary_key=True)

    relationship_id = db.Column(db.Integer, db.ForeignKey("relationships.id"), nullable=False)
    relationship = db.relationship("Relationship", back_populates="crisp_scores")

    credibility = db.Column(db.Integer, nullable=False)
    reliability = db.Column(db.Integer, nullable=False)
    intimacy = db.Column(db.Integer, nullable=False)
    self_orientation = db.Column(db.Integer, nullable=False)

    notes = db.Column(db.Text)
    total_score = db.Column(db.Float)

    def __repr__(self) -> str:
        """Readable representation for debugging.

        Returns:
            str: Summary of the score and associated relationship.
        """
        return f"<CRISPScore Relationship={self.relationship_id} Total={self.total_score}>"

    def calculate_total(self) -> None:
        """Calculate the CRISP total score using the standard formula.

        Formula:
            (C + R + I) / S, where S is self-orientation.
            If S is zero, it falls back to sum of other metrics.

        Sets:
            total_score: Computed float value.
        """
        c = self.credibility
        r = self.reliability
        i = self.intimacy
        s = self.self_orientation

        if s == 0:
            self.total_score = float(c + r + i)
        else:
            self.total_score = float(c + r + i) / s

    def save(self) -> "CRISPScore":
        """Override save to compute total score before persisting.

        Returns:
            CRISPScore: The saved instance.
        """
        logger.info("Calculating CRISP total score before saving.")
        self.calculate_total()
        return super().save()
