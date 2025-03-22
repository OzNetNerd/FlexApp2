from models.base import db, BaseModel
from sqlalchemy.orm import foreign


import logging

logger = logging.getLogger(__name__)

class Contact(db.Model, BaseModel):
    __tablename__ = 'contacts'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    company = db.relationship("Company", back_populates="contacts")
    notes = db.relationship(
        'Note',
        primaryjoin="and_(Note.notable_id == foreign(Contact.id), Note.notable_type == 'Contact')"
    )

    __field_order__ = [
        {
            'name': 'first_name',
            'label': 'First Name',
            'type': 'text',
            'required': True,
            'section': 'Basic Info'
        },
        {
            'name': 'last_name',
            'label': 'Last Name',
            'type': 'text',
            'required': True,
            'section': 'Basic Info'
        },
        {
            'name': 'email',
            'label': 'Email',
            'type': 'email',
            'section': 'Contact'
        },
        {
            'name': 'phone',
            'label': 'Phone',
            'type': 'text',
            'section': 'Contact'
        },
        {
            'name': 'company_name',
            'label': 'Company',
            'type': 'text',
            'section': 'Company Info'
        },
        {
            'name': 'created_at',
            'label': 'Created At',
            'type': 'text',
            'section': 'Record Info',
            "readonly": True,
        },
        {
            'name': 'updated_at',
            'label': 'Updated At',
            'type': 'text',
            'section': 'Record Info',
            "readonly": True,

        }
    ]

    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name}>'

    @property
    def full_name(self):
        logger.debug(f"Accessing full name for {self.first_name} {self.last_name}")
        return f"{self.first_name} {self.last_name}"
