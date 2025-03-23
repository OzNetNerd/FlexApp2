from app.models.base import db, BaseModel
from app.models.company_capability import CompanyCapability


class Capability(db.Model, BaseModel):
    __tablename__ = "capabilities"

    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey("capability_categories.id"), nullable=False
    )

    company_capabilities = db.relationship(
        "CompanyCapability",
        back_populates="capability",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @property
    def companies(self):
        """Return all Company objects using this capability."""
        return [cc.company for cc in self.company_capabilities]

    def __repr__(self):
        return f"<Capability {self.name}>"
