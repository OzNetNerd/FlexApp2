import logging
from app.models.base import db, BaseModel

logger = logging.getLogger(__name__)


class CompanyCapability(BaseModel):
    """Association table mapping companies to capabilities.

    Defines a many-to-many relationship between Company and Capability
    via explicit association, allowing for metadata or constraints on the link.

    Attributes:
        company_id (int): FK to the Company this capability belongs to.
        capability_id (int): FK to the associated Capability.
        company (Company): The related Company object.
        capability (Capability): The related Capability object.
    """

    __tablename__ = "company_capabilities"

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    capability_id = db.Column(db.Integer, db.ForeignKey("capabilities.id"), nullable=False)

    __table_args__ = (db.UniqueConstraint("company_id", "capability_id", name="uq_company_capability"),)

    company = db.relationship("Company", back_populates="company_capabilities")
    capability = db.relationship("Capability", back_populates="company_capabilities")

    def __repr__(self) -> str:
        """String representation for debugging purposes.

        Returns:
            str: Readable representation showing company and capability IDs.
        """
        return f"<CompanyCapability company={self.company_id} capability={self.capability_id}>"
