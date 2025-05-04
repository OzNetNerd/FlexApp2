# app/models/__init__.py

"""
Centralized imports for all SQLAlchemy models and the `db` instance.
"""

import logging

from app.models.base import BaseModel, db

from app.models.capability import Capability
from app.models.capability_category import CapabilityCategory
from app.models.company_capability import CompanyCapability
from app.models.pages.crisp import Crisp
from app.models.mixins import ValidatorMixin
from app.models.relationship import Relationship
from app.models.table_config import TableConfig

from app.models.pages.company import Company
from app.models.pages.contact import Contact
from app.models.pages.note import Note
from app.models.pages.opportunity import Opportunity
from app.models.pages.srs import ReviewHistory, SRS
from app.models.pages.setting import Setting
from app.models.pages.task import Task
from app.models.pages.user import User

logger = logging.getLogger(__name__)

__all__ = [
    "db",
    "BaseModel",
    "CapabilityCategory",
    "Capability",
    "CompanyCapability",
    "Company",
    "Contact",
    "Crisp",
    "ValidatorMixin",
    "Note",
    "Opportunity",
    "Relationship",
    "ReviewHistory",
    "Setting",
    "SRS",
    "TableConfig",
    "Task",
    "User",
]
