from models.base import db, BaseModel


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
    relationships = db.relationship('Relationship', back_populates='contact', cascade='all, delete-orphan')
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

    @property
    def crisp_summary(self):
        """
        Returns the average CRISP total score across all user relationships for this contact.
        """
        all_scores = [
            score.total_score
            for relationship in self.relationships
            for score in relationship.crisp_scores
            if score.total_score is not None
        ]

        if not all_scores:
            return None

        return round(sum(all_scores) / len(all_scores), 2)
