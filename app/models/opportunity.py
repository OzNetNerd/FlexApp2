from models.base import db, BaseModel
import logging

logger = logging.getLogger(__name__)


class Opportunity(db.Model, BaseModel):
    __tablename__ = 'opportunities'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='New')
    stage = db.Column(db.String(50), default='Prospecting')
    value = db.Column(db.Float, default=0.0)

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    notes = db.relationship(
        'Note',
        primaryjoin="and_(Note.notable_id == foreign(Opportunity.id), Note.notable_type == 'Opportunity')"
    )

    __field_order__ = [
        {"name": "name", "label": "Name", "type": "text", "required": True, "section": "Opportunity Info"},
        {"name": "description", "label": "Description", "type": "textarea", "section": "Opportunity Info"},
        {"name": "company.name", "label": "Company Name", "type": "text", "readonly": True, "section": "Opportunity Info"},
        {"name": "stage", "label": "Stage", "type": "text", "section": "Details"},
        {"name": "status", "label": "Status", "type": "text", "section": "Details"},
        {"name": "value", "label": "Value", "type": "number", "section": "Details"},
        {"name": "created_at", "label": "Created At", "type": "datetime", "readonly": True, "section": "Record Info"},
        {"name": "updated_at", "label": "Updated At", "type": "datetime", "readonly": True, "section": "Record Info"}
    ]

    def __repr__(self):
        return f'<Opportunity {self.name}>'

    def save(self):
        logger.debug(f"Saving opportunity with name {self.name} and status {self.status}")
        super().save()
        logger.info(f"Opportunity '{self.name}' saved successfully.")

    def delete(self):
        logger.debug(f"Deleting opportunity with name {self.name}")
        super().delete()
        logger.info(f"Opportunity '{self.name}' deleted successfully.")

    @property
    def crisp_summary(self):
        """
        Average CRISP score across all contacts involved in this opportunity.
        """
        contacts = {rel.contact for note in self.notes for rel in note.author.relationships}
        scores = [c.crisp_summary for c in contacts if c.crisp_summary is not None]

        if not scores:
            return None

        return round(sum(scores) / len(scores), 2)
