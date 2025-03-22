from app.models.base import db, BaseModel
import logging

logger = logging.getLogger(__name__)

class CompanyCapability(db.Model, BaseModel):
    __tablename__ = 'company_capabilities'

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    capability_id = db.Column(db.Integer, db.ForeignKey('capabilities.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('company_id', 'capability_id', name='uq_company_capability'),
    )

    company = db.relationship('Company', back_populates='company_capabilities')
    capability = db.relationship('Capability', back_populates='company_capabilities')

    def __repr__(self):
        return f'<CompanyCapability company={self.company_id} capability={self.capability_id}>'
