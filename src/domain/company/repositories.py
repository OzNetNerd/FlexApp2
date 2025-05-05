"""
Repository interfaces for the Company domain.

This module defines the repository interfaces that provide data access
for Company domain entities, following DDD principles.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from src.domain.company.entities import Company
from src.domain.shared.interfaces.repository import Repository


class CompanyRepository(Repository[Company], ABC):
    """
    Repository interface for Company entities.

    Provides methods for retrieving and persisting Company domain objects.
    """

    @abstractmethod
    async def get_by_id(self, company_id: int) -> Optional[Company]:
        """
        Retrieve a company by its ID.

        Args:
            company_id: The ID of the company to retrieve

        Returns:
            Optional[Company]: The company if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_id_with_details(self, company_id: int) -> Optional[Company]:
        """
        Retrieve a company with additional details by its ID.

        This method loads additional details like description, employee count,
        and revenue that might not be loaded by the basic get_by_id method.

        Args:
            company_id: The ID of the company to retrieve

        Returns:
            Optional[Company]: The company with details if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_paginated(self, limit: int = 20, offset: int = 0, filters: Optional[Dict[str, Any]] = None) -> List[Company]:
        """
        Retrieve a paginated list of companies with optional filtering.

        Args:
            limit: Maximum number of companies to return
            offset: Number of companies to skip
            filters: Optional dictionary of filters to apply

        Returns:
            List[Company]: Paginated list of company entities
        """
        pass

    @abstractmethod
    async def find_by_customer_id(self, customer_id: int) -> List[Company]:
        """
        Find companies associated with a specific customer.

        Args:
            customer_id: ID of the customer whose companies to retrieve

        Returns:
            List[Company]: List of companies associated with the customer
        """
        pass
