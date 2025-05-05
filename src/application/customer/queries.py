"""Customer query handlers."""

from typing import List, Optional
from src.domain.customer.repositories import CustomerRepository
from src.application.customer.dto import CustomerDTO


class CustomerQueryHandler:
    """
    Query handler for customer data.

    Handles queries that retrieve customer data.
    """

    def __init__(self, customer_repository: CustomerRepository):
        """Initialize with a customer repository."""
        self.customer_repository = customer_repository

    def get_customer_by_id(self, id: int) -> Optional[CustomerDTO]:
        """
        Get a customer by ID.

        Args:
            id: The customer ID to retrieve

        Returns:
            A DTO of the customer or None if not found
        """
        customer = self.customer_repository.get_by_id(id)
        if not customer:
            return None
        return CustomerDTO.from_entity(customer)

    def get_all_customers(self) -> List[CustomerDTO]:
        """
        Get all customers.

        Returns:
            A list of customer DTOs
        """
        customers = self.customer_repository.get_all()
        return [CustomerDTO.from_entity(customer) for customer in customers]

    def search_customers_by_name(self, query: str) -> List[CustomerDTO]:
        """
        Search for customers by name.

        Args:
            query: The search string to match against customer names

        Returns:
            A list of customer DTOs matching the search criteria
        """
        customers = self.customer_repository.search_by_name(query)
        return [CustomerDTO.from_entity(customer) for customer in customers]

    def get_customers_by_company(self, company_id: int) -> List[CustomerDTO]:
        """
        Get customers associated with a specific company.

        Args:
            company_id: The ID of the company

        Returns:
            A list of customer DTOs associated with the company
        """
        customers = self.customer_repository.get_by_company(company_id)
        return [CustomerDTO.from_entity(customer) for customer in customers]