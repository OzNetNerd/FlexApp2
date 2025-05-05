# MIGRATED
# app/models/company.py

from app.models.base import BaseModel, db
from app.utils.app_logging import get_logger

logger = get_logger()


class Company(BaseModel):
    name = db.Column(
        db.String(100),
        nullable=False,
    )

    description = db.Column(
        db.Text,
    )

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
        return f"<Company {self.name!r}>"
