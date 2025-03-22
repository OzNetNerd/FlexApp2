from models.base import db, BaseModel

class CapabilityCategory(db.Model, BaseModel):
    __tablename__ = 'capability_categories'

    name = db.Column(db.String(100), nullable=False, unique=True)

    capabilities = db.relationship('Capability', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<CapabilityCategory {self.name}>'
