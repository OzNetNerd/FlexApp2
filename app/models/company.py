from models.base import db, BaseModel
from sqlalchemy.orm import foreign
from models.note import Note
import logging

logger = logging.getLogger(__name__)


class Company(db.Model, BaseModel):
    __tablename__ = 'companies'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Relationships
    contacts = db.relationship("Contact", back_populates="company")
    opportunities = db.relationship("Opportunity", backref="company", lazy="dynamic")
    notes = db.relationship(
        'Note',
        primaryjoin="and_(Note.notable_id == foreign(Company.id), Note.notable_type == 'Company')"
    )

    # New relationship for capabilities
    company_capabilities = db.relationship(
        "CompanyCapability",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    @property
    def capabilities(self):
        """Return all Capability objects linked to this company."""
        return [cc.capability for cc in self.company_capabilities]

    __field_order__ = [
        {
            'name': 'name',
            'label': 'Name',
            'type': 'text',
            'section': 'About',
            'required': True
        },
        {
            'name': 'description',
            'label': 'Description',
            'type': 'text',
            'section': 'About'
        },
        {
            'name': 'created_at',
            'label': 'Created At',
            'type': 'text',
            "readonly": True,
            'section': 'Record Info'
        },
        {
            'name': 'updated_at',
            'label': 'Updated At',
            'type': 'text',
            "readonly": True,
            'section': 'Record Info'
        }
    ]

    def __repr__(self):
        return f'<Company {self.name}>'

    @staticmethod
    def search_by_name(query):
        """Search companies by name for mentions."""
        logger.debug(f"Searching for companies with name starting with '{query}'")
        result = Company.query.filter(Company.name.ilike(f'{query}%')).all()
        logger.debug(f"Found {len(result)} companies matching the query '{query}'")
        return result

    @property
    def crisp_summary(self):
        """
        Average CRISP score across all contacts at this company.
        """
        scores = [c.crisp_summary for c in self.contacts if c.crisp_summary is not None]

        if not scores:
            return None

        return round(sum(scores) / len(scores), 2)
