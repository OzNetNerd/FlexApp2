from app.utils.app_logging import get_logger
logger = get_logger()

# Import base first to initialize db
from .base import db

# Association Table for Many-to-Many relationship between Contact and User
contact_user_association = db.Table(
    "contact_user_association",
    db.Column("contact_id", db.Integer, db.ForeignKey("contacts.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
)

# Import dependent models first
from .capability_category import CapabilityCategory
from .capability import Capability
from .company_capability import CompanyCapability

# Core business models
from .user import User
from .company import Company
from .contact import Contact
from .opportunity import Opportunity
from .note import Note
from .task import Task
from .table_config import TableConfig
from .relationship import Relationship
from .crisp_score import CRISPScore
from .setting import Setting

__all__ = [
    "db",
    "User",
    "Company",
    "Contact",
    "Opportunity",
    "Note",
    "Task",
    "TableConfig",
    "Relationship",
    "CRISPScore",
    "Setting",  # Added to export list
    "contact_user_association",
    "CapabilityCategory",
    "Capability",
    "CompanyCapability",
]

# Log that the models module has been loaded
logger.info(f"Loaded models: {', '.join(__all__)}")
