from app.models.base import db, BaseModel
from sqlalchemy.orm import foreign
from app.models.note import Note
import logging

logger = logging.getLogger(__name__)

class Company(db.Model, BaseModel):
    """Represents a company in the CRM system.

    Stores metadata about a company and links to its contacts, opportunities,
    notes, capabilities, and scoring summaries.

    Attributes:
        name (str): Display name of the company.
        description (str): Additional details about the company.
        contacts (list[Contact]): Related contacts.
        opportunities (list[Opportunity]): Related opportunities.
        notes (list[Note]): Notes linked via polymorphic relationship.
        company_capabilities (list[CompanyCapability]): Capabilities offered.
        __field_order__ (list[dict]): UI metadata for rendering forms.
    """

    __tablename__ = "companies"

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

    __field_order__ = [
        {"name": "name", "label": "Name", "type": "text", "section": "About", "required": True},
        {"name": "description", "label": "Description", "type": "text", "section": "About"},
        {"name": "created_at", "label": "Created At", "type": "text", "readonly": True, "section": "Record Info"},
        {"name": "updated_at", "label": "Updated At", "type": "text", "readonly": True, "section": "Record Info"},
    ]

    def __repr__(self) -> str:
        """String representation for debugging.

        Returns:
            str: A readable company identifier.
        """
        return f"<Company {self.name}>"

    @staticmethod
    def search_by_name(query: str) -> list:
        """Search for companies whose name starts with a given string.

        Args:
            query: Partial name to search.

        Returns:
            list: List of Company objects matching the query.
        """
        logger.debug(f"Searching for companies with name starting with '{query}'")
        result = Company.query.filter(Company.name.ilike(f"{query}%")).all()
        logger.debug(f"Found {len(result)} companies matching the query '{query}'")
        return result

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
