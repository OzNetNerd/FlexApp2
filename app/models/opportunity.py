import logging
from app.models.base import db, BaseModel
from app.routes.base.components.form_handler import Tab, TabSection, TabEntry

logger = logging.getLogger(__name__)


class Opportunity(BaseModel):
    """Represents a sales opportunity linked to a company.

    Opportunities track deal stages, potential value, and related notes.

    Attributes:
        name (str): Title of the opportunity.
        description (str): Summary or notes about the opportunity.
        status (str): Current status (e.g., New, Won, Lost).
        stage (str): Sales pipeline stage (e.g., Prospecting).
        value (float): Estimated deal value.
        company_id (int): FK to the related company.
        notes (list[Note]): Notes linked via polymorphic relationship.
        __field_order__ (list[dict]): Field metadata for UI rendering.
    """

    __tablename__ = "opportunities"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="New")
    stage = db.Column(db.String(50), default="Prospecting")
    value = db.Column(db.Float, default=0.0)

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))

    notes = db.relationship(
        "Note",
        primaryjoin="and_(Note.notable_id == foreign(Opportunity.id), Note.notable_type == 'Opportunity')",
    )

    # Details section
    details_section = TabSection(section_name="Details", entries=[
        TabEntry(entry_name="name", label="Name", type="text", required=True),
        TabEntry(entry_name="description", label="Description", type="textarea"),
        TabEntry(entry_name="company.name", label="Company Name", type="text",),
    ])

    # Pipeline section
    pipeline_section = TabSection(section_name="Pipeline", entries=[
        TabEntry(entry_name="stage", label="Stage", type="text", required=True),
        TabEntry(entry_name="status", label="Status", type="text"),
    ])

    # Financial section
    financial_section = TabSection(section_name="Financial", entries=[
        TabEntry(entry_name="value", label="Value", type="number", required=True),
    ])

    # Crisp section
    crisp_section = TabSection(section_name="CRISP", entries=[
        TabEntry(entry_name="crisp", label="CRISP", type="string", required=True),
    ])


    overview_tab = Tab(tab_name='Overview', sections=[details_section, pipeline_section])
    deal_tab = Tab(tab_name='Deal', sections=[financial_section, crisp_section])

    __tabs__ = [overview_tab, deal_tab]

    def __repr__(self) -> str:
        """Readable string representation.

        Returns:
            str: Identifier showing the opportunity name.
        """
        return f"<Opportunity {self.name}>"

    def save(self) -> "Opportunity":
        """Persist opportunity to the database with logging.

        Returns:
            Opportunity: The saved instance.
        """
        logger.debug(f"Saving opportunity with name {self.name} and status {self.status}")
        super().save()
        logger.info(f"Opportunity '{self.name}' saved successfully.")
        return self

    def delete(self) -> None:
        """Remove opportunity from the database with logging."""
        logger.debug(f"Deleting opportunity with name {self.name}")
        super().delete()
        logger.info(f"Opportunity '{self.name}' deleted successfully.")

    @property
    def crisp_summary(self) -> float | None:
        """Compute average CRISP score for all related contacts.

        Returns:
            float | None: Average CRISP score across all involved contacts.
        """
        contacts = {rel.contact for note in self.notes for rel in note.author.relationships}
        scores = [c.crisp_summary for c in contacts if c.crisp_summary is not None]

        if not scores:
            return None

        return round(sum(scores) / len(scores), 2)
