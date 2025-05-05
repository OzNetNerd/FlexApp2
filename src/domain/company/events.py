"""
Domain events for the company aggregate.

This module defines events that occur within the company domain.
These events represent important state changes in company entities.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass(frozen=True)
class CompanyCreated:
    """
    Event raised when a new company is created.

    Attributes:
        company_id: The ID of the created company
        timestamp: When the event occurred
    """
    company_id: int
    timestamp: datetime = datetime.now()


@dataclass(frozen=True)
class CompanyUpdated:
    """
    Event raised when a company is updated.

    Attributes:
        company_id: The ID of the updated company
        timestamp: When the event occurred
    """
    company_id: int
    timestamp: datetime = datetime.now()


@dataclass(frozen=True)
class CompanyDeleted:
    """
    Event raised when a company is deleted.

    Attributes:
        company_id: The ID of the deleted company
        timestamp: When the event occurred
    """
    company_id: int
    timestamp: datetime = datetime.now()