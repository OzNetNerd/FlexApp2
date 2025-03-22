from app.models.base import db, BaseModel
import logging

logger = logging.getLogger(__name__)

class Relationship(db.Model, BaseModel):
    __tablename__ = 'relationships'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)

    user = db.relationship('User', back_populates='relationships')
    contact = db.relationship('Contact', back_populates='relationships')

    # History of CRISP scores for this relationship
    crisp_scores = db.relationship('CRISPScore', back_populates='relationship', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'contact_id', name='_user_contact_uc'),
    )

    def __repr__(self):
        return f'<Relationship User={self.user_id} Contact={self.contact_id}>'
