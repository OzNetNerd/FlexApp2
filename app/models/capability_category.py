# MIGRATED
from app.models.base import BaseModel, db


class CapabilityCategory(BaseModel):
    __tablename__ = "capability_categories"

    # Add this primary key column
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False, unique=True)

    capabilities = db.relationship("Capability", backref="category", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<CapabilityCategory {self.name}>"
