# models/company.py

from app.models.base import BaseModel, db
from app.utils.app_logging import get_logger

logger = get_logger()


class Company(BaseModel):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    contacts = db.relationship("Contact", back_populates="company")
    opportunities = db.relationship("Opportunity", backref="company", lazy="dynamic")

    notes = db.relationship(
        "Note",
        primaryjoin="and_(Note.notable_id == foreign(Company.id), Note.notable_type == 'Company')",
    )

    company_capabilities = db.relationship(
        "CompanyCapability",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @property
    def capabilities(self) -> list:
        """Get all capabilities associated with this company.

        Returns:
            list: A list of Capability instances linked via CompanyCapability.
        """
        return [cc.capability for cc in self.company_capabilities]

    @property
    def crisp_summary(self) -> float | None:
        """Average CRISP score across all contacts at this company.

        Returns:
            float | None: Rounded average score, or None if no scores exist.
        """
        scores = [c.crisp_summary for c in self.contacts if c.crisp_summary is not None]
        if not scores:
            return None
        return round(sum(scores) / len(scores), 2)

    def __repr__(self) -> str:
        """String representation for debugging.

        Returns:
            str: A readable company identifier.
        """
        return f"<Company {self.name!r}>"

    @staticmethod
    def search_by_name(query: str) -> list:
        """Search for companies whose name starts with a given string.

        Args:
            query: Partial name to search.

        Returns:
            list: List of Company objects matching the query.
        """
        logger.info(f"Searching for companies with name starting with {query!r}")
        result = Company.query.filter(Company.name.ilike(f"{query}%")).all()
        logger.info(f"Found {len(result)} companies matching the query {query!r}")
        return result
