"""
Customer DataLoader implementation.

This module provides DataLoader functionality for Customer entities.
"""
from typing import List, Optional
from interfaces.graphql.dataloaders.base import BaseLoader
from domain.customer.entities import Customer


class CustomerLoader(BaseLoader[Customer, int]):
    """
    DataLoader for Customer entities.

    This loader handles efficient loading of Customer entities by ID
    and provides specialized loading methods for customer-specific
    relationships.
    """

    async def load_many(self, customer_ids: List[int]) -> List[Optional[Customer]]:
        """
        Load multiple customers by their IDs.

        Args:
            customer_ids: List of customer IDs to load

        Returns:
            List[Optional[Customer]]: List of loaded customer entities
        """
        return await self.load_by_ids(
            customer_ids,
            lambda uow: uow.customer_repository
        )

    async def load_one(self, customer_id: int) -> Optional[Customer]:
        """
        Load a single customer by ID.

        Args:
            customer_id: ID of the customer to load

        Returns:
            Optional[Customer]: The loaded customer or None if not found
        """
        result = await self.load_many([customer_id])
        return result[0] if result else None

    async def load_by_company_id(self, company_id: int) -> List[Customer]:
        """
        Load customers associated with a specific company.

        Args:
            company_id: ID of the company whose customers to load

        Returns:
            List[Customer]: List of customers associated with the company
        """
        with self.unit_of_work:
            repository = self.unit_of_work.customer_repository
            return repository.find_by_company_id(company_id)