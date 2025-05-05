"""
Opportunity DataLoader implementation.

This module provides DataLoader functionality for Opportunity entities.
"""
from typing import List, Optional
from src.interfaces.graphql.dataloaders.base import BaseLoader
from src.domain.opportunity.entities import Opportunity


class OpportunityLoader(BaseLoader[Opportunity, int]):
    """
    DataLoader for Opportunity entities.

    This loader handles efficient loading of Opportunity entities by ID
    and provides specialized loading methods for opportunity-specific
    relationships.
    """

    async def load_many(self, opportunity_ids: List[int]) -> List[Optional[Opportunity]]:
        """
        Load multiple opportunities by their IDs.

        Args:
            opportunity_ids: List of opportunity IDs to load

        Returns:
            List[Optional[Opportunity]]: List of loaded opportunity entities
        """
        return await self.load_by_ids(
            opportunity_ids,
            lambda uow: uow.opportunity_repository
        )

    async def load_one(self, opportunity_id: int) -> Optional[Opportunity]:
        """
        Load a single opportunity by ID.

        Args:
            opportunity_id: ID of the opportunity to load

        Returns:
            Optional[Opportunity]: The loaded opportunity or None if not found
        """
        result = await self.load_many([opportunity_id])
        return result[0] if result else None

    async def load_by_company_id(self, company_id: int) -> List[Opportunity]:
        """
        Load opportunities associated with a specific company.

        Args:
            company_id: ID of the company whose opportunities to load

        Returns:
            List[Opportunity]: List of opportunities associated with the company
        """
        with self.unit_of_work:
            repository = self.unit_of_work.opportunity_repository
            return repository.find_by_company_id(company_id)

    async def load_by_customer_id(self, customer_id: int) -> List[Opportunity]:
        """
        Load opportunities associated with a specific customer.

        Args:
            customer_id: ID of the customer whose opportunities to load

        Returns:
            List[Opportunity]: List of opportunities associated with the customer
        """
        with self.unit_of_work:
            repository = self.unit_of_work.opportunity_repository
            return repository.find_by_customer_id(customer_id)