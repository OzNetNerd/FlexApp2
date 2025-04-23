# app/models/__init__.py

"""
Centralized imports for all SQLAlchemy models and the `db` instance.
"""

import logging

from .base import BaseModel, db
from .capability import Capability
from .capability_category import CapabilityCategory
from .company import Company
from .company_capability import CompanyCapability
from .contact import Contact
from .crisp_score import CRISPScore
from .mixins import ValidatorMixin
from .note import Note
from .opportunity import Opportunity
from .relationship import Relationship
from .review_history import ReviewHistory
from .setting import Setting
from .srs_item import SRSItem
from .table_config import TableConfig
from .task import Task
from .user import User

logger = logging.getLogger(__name__)

__all__ = [
    "db",
    "BaseModel",
    "CapabilityCategory",
    "Capability",
    "CompanyCapability",
    "Company",
    "Contact",
    "CRISPScore",
    "ValidatorMixin",
    "Note",
    "Opportunity",
    "Relationship",
    "ReviewHistory",
    "Setting",
    "SRSItem",
    "TableConfig",
    "Task",
    "User",
]
