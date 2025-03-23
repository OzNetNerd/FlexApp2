import logging

# Use the same logger as the Flask app
logger = logging.getLogger(__name__)

# Import base first to initialize db
from .base import db

# Association Table
contact_user_association = db.Table(
    'contact_user_association',
    db.Column('contact_id', db.Integer, db.ForeignKey('contacts.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

# Import new models in dependency-safe order
from .capability_category import CapabilityCategory
from .capability import Capability
from .company_capability import CompanyCapability

# Then import core business models
from .user import User
from .company import Company
from .contact import Contact
from .opportunity import Opportunity
from .note import Note
from .table_config import TableConfig
from .relationship import Relationship
from .crisp_score import CRISPScore

__all__ = [
    'db',
    'User',
    'Company',
    'Contact',
    'Opportunity',
    'Note',
    'TableConfig',
    'Relationship',
    'CRISPScore',
    'contact_user_association'
]

# Log that the module is being loaded
logger.debug(f"Loaded models: {', '.join(__all__)}")
