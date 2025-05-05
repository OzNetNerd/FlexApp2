# MIGRATED
# company_capability.py

from app.models.base import BaseModel, db
from app.utils.app_logging import get_logger

logger = get_logger()


class CompanyCapability(BaseModel):
    """Association table mapping companies to capabilities."""

    __tablename__ = "company_capabilities"

    # Add this primary key
    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    capability_id = db.Column(db.Integer, db.ForeignKey("capabilities.id"), nullable=False)

    __table_args__ = (db.UniqueConstraint("company_id", "capability_id", name="uq_company_capability"),)

    company = db.relationship("Company", back_populates="company_capabilities")
    capability = db.relationship("Capability", back_populates="company_capabilities")

    def __repr__(self) -> str:
        return f"<CompanyCapability company={self.company_id} capability={self.capability_id}>"
