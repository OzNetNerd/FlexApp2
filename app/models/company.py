import logging
from app.models.base import db, BaseModel
from app.models.note import Note
from app.routes.base.components.form_handler import Tab, TabSection, TabEntry

logger = logging.getLogger(__name__)


class Company(BaseModel):
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

    # Company Details section
    company_details_section = TabSection(section_name="Company Details", entries=[
        TabEntry(entry_name="name", label="Name", type="text", required=True),
        TabEntry(entry_name="description", label="Description", type="text"),
    ])

    # CRISP Score section
    crisp_score_section = TabSection(section_name="CRISP Score", entries=[
        TabEntry(entry_name="crisp", label="CRISP", type="custom"),
    ])

    # About tab
    about_tab = Tab(tab_name="About", sections=[company_details_section])

    # Insights tab
    insights_tab = Tab(tab_name="Insights", sections=[crisp_score_section])

    __tabs__ = [about_tab, insights_tab]

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
