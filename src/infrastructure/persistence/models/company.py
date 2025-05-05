"""ORM models for the company domain."""

from src.infrastructure.persistence.models.base import BaseModel
from src.infrastructure.flask.extensions import db


class Company(BaseModel):
    """
    ORM model for companies.

    Maps the Company domain entity to the database.
    """

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    contacts = db.relationship("Contact", back_populates="company")
    opportunities = db.relationship("Opportunity", backref="company", lazy="dynamic")
    notes = db.relationship(
        "Note",
        primaryjoin=("and_(Note.notable_id == foreign(Company.id), " "Note.notable_type == 'Company')"),
    )
    company_capabilities = db.relationship(
        "CompanyCapability",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        """Return string representation of the company."""
        return f"<Company {self.name!r}>"


class CompanyCapability(BaseModel):
    """
    ORM model for company capabilities.

    Maps the CompanyCapability domain entity to the database.
    """

    __tablename__ = "company_capabilities"

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    capability_id = db.Column(db.Integer, db.ForeignKey("capabilities.id"), nullable=False)
    level = db.Column(db.String(50))  # e.g., "Expert", "Proficient", "Beginner"

    company = db.relationship("Company", back_populates="company_capabilities")
    capability = db.relationship("Capability")
