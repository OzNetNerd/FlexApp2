"""
Company DataLoader implementation.

This module provides DataLoader functionality for Company entities.
"""
from typing import List, Optional
from src.interfaces.graphql.dataloaders.base import BaseLoader
from src.domain.company.entities import Company


class CompanyLoader(BaseLoader[Company, int]):
    """
    DataLoader for Company entities.

    This loader handles efficient loading of Company entities by ID
    and provides specialized loading methods for company-specific
    relationships.
    """

    async def load_many(self, company_ids: List[int]) -> List[Optional[Company]]:
        """
        Load multiple companies by their IDs.

        Args:
            company_ids: List of company IDs to load

        Returns:
            List[Optional[Company]]: List of loaded company entities
        """
        return await self.load_by_ids(
            company_ids,
            lambda uow: uow.company_repository
        )

    async def load_one(self, company_id: int) -> Optional[Company]:
        """
        Load a single company by ID.

        Args:
            company_id: ID of the company to load

        Returns:
            Optional[Company]: The loaded company or None if not found
        """
        result = await self.load_many([company_id])
        return result[0] if result else None

    async def load_by_customer_id(self, customer_id: int) -> List[Company]:
        """
        Load companies associated with a specific customer.

        Args:
            customer_id: ID of the customer whose companies to load

        Returns:
            List[Company]: List of companies associated with the customer
        """
        with self.unit_of_work:
            repository = self.unit_of_work.company_repository
            return repository.find_by_customer_id(customer_id)