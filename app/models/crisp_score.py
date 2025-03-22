from models.base import db, BaseModel
import logging

logger = logging.getLogger(__name__)

class CRISPScore(db.Model, BaseModel):
    __tablename__ = 'crisp_scores'

    relationship_id = db.Column(db.Integer, db.ForeignKey('relationships.id'), nullable=False)
    relationship = db.relationship('Relationship', back_populates='crisp_scores')

    c_score = db.Column(db.Integer, nullable=False)  # Credibility
    r_score = db.Column(db.Integer, nullable=False)  # Reliability
    i_score = db.Column(db.Integer, nullable=False)  # Intimacy
    s_score = db.Column(db.Integer, nullable=False)  # Self-orientation
    p_score = db.Column(db.Integer, nullable=False)  # Personalization

    notes = db.Column(db.Text)
    total_score = db.Column(db.Float)

    def __repr__(self):
        return f'<CRISPScore Relationship={self.relationship_id} Total={self.total_score}>'

    def calculate_total(self):
        """Calculate the total CRISP score."""
        if self.s_score == 0:
            self.total_score = float(self.c_score + self.r_score + self.i_score + self.p_score)
        else:
            self.total_score = float(self.c_score + self.r_score + self.i_score + self.p_score) / self.s_score

    def save(self):
        """Save with calculated total score."""
        logger.debug("Calculating CRISP total score before saving.")
        self.calculate_total()
        super().save()
