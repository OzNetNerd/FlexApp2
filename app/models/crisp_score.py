from app.models.base import db, BaseModel
import logging

logger = logging.getLogger(__name__)

class CRISPScore(db.Model, BaseModel):
    """Represents a CRISP trust metric for a contact-user relationship.

    CRISP = Credibility, Reliability, Intimacy, Self-Orientation.
    A higher score reflects stronger trust in the relationship.

    Attributes:
        relationship_id (int): Foreign key to the related relationship.
        credibility (int): Score for credibility.
        reliability (int): Score for reliability.
        intimacy (int): Score for intimacy.
        self_orientation (int): Score for self-orientation (lower is better).
        notes (str): Optional notes.
        total_score (float): Computed trust score.
    """

    __tablename__ = "crisp_scores"

    relationship_id = db.Column(
        db.Integer, db.ForeignKey("relationships.id"), nullable=False
    )
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

    def save(self):
        """Override save to compute total score before persisting.

        Returns:
            CRISPScore: The saved instance.
        """
        logger.debug("Calculating CRISP total score before saving.")
        self.calculate_total()
        return super().save()
