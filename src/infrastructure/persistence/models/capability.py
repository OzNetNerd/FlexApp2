"""
SQLAlchemy models for the capability domain.

These models map the domain entities to database tables, focusing solely on
persistence concerns without domain logic.
"""

from src.infrastructure.persistence.models.base import BaseModel, db
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class CapabilityCategory(BaseModel):
    """
    Database model for capability categories.

    Attributes:
        id: Primary key.
        name: Category name.
        capabilities: Relationship to child capabilities.
    """

    name = db.Column(db.String(100), nullable=False, unique=True)
    capabilities = db.relationship("Capability", backref="category", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<CapabilityCategory id={self.id} name={self.name!r}>"


class Capability(BaseModel):
    """
    Database model for capabilities.

    Attributes:
        id: Primary key.
        name: Capability name.
        category_id: Foreign key to the parent category.
        company_capabilities: Relationship to company associations.
    """

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
        """
        Get companies that have this capability.

        Returns:
            List of companies with this capability.
        """
        return [cc.company for cc in self.company_capabilities]

    def __repr__(self) -> str:
        return f"<Capability id={self.id} name={self.name!r}>"


class CompanyCapability(BaseModel):
    """
    Association table mapping companies to capabilities.

    Attributes:
        id: Primary key.
        company_id: Foreign key to the company.
        capability_id: Foreign key to the capability.
        company: Relationship to the company.
        capability: Relationship to the capability.
    """

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    capability_id = db.Column(db.Integer, db.ForeignKey("capabilities.id"), nullable=False)

    # Ensure each company-capability pair is unique
    __table_args__ = (db.UniqueConstraint("company_id", "capability_id", name="uq_company_capability"),)

    company = db.relationship("Company", back_populates="company_capabilities")
    capability = db.relationship("Capability", back_populates="company_capabilities")

    def __repr__(self) -> str:
        return f"<CompanyCapability company_id={self.company_id} capability_id={self.capability_id}>"
