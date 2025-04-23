from app.models.base import BaseModel, db
from app.models.company_capability import CompanyCapability


class Capability(BaseModel):
    __tablename__ = "capabilities"

    # Add this primary key column
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("capability_categories.id"), nullable=False)

    company_capabilities = db.relationship(
        "CompanyCapability",
        back_populates="capability",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @property
    def companies(self) -> list:
        return [cc.company for cc in self.company_capabilities]

    def __repr__(self) -> str:
        return f"<Capability {self.name}>"
