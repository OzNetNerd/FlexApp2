import logging

# Use the same logger as the Flask app
logger = logging.getLogger(__name__)

# Import base first to initialize db
from .base import db

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

__all__ = [
    'db',
    'CapabilityCategory',
    'Capability',
    'CompanyCapability',
    'User',
    'Company',
    'Contact',
    'Opportunity',
    'Note',
    'TableConfig'
]

# Log that the module is being loaded
logger.debug(f"Loaded models: {', '.join(__all__)}")
