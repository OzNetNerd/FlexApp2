# src/interfaces/graphql/customer/queries.py
"""GraphQL queries for customer operations."""

import strawberry
from typing import List, Optional
from src.application.customer.queries import CustomerQueryHandler
from src.interfaces.graphql.customer.types import Customer


@strawberry.type
class CustomerQueries:
    """GraphQL query resolvers for customer operations."""

    def __init__(self, query_handler: CustomerQueryHandler):
        """Initialize with a query handler."""
        self.query_handler = query_handler

    @strawberry.field
    def customer(self, id: int) -> Optional[Customer]:
        """Get a customer by ID."""
        customer_dto = self.query_handler.get_customer_by_id(id)
        if not customer_dto:
            return None
        return Customer.from_dto(customer_dto)

    @strawberry.field
    def customers(self) -> List[Customer]:
        """Get all customers."""
        customer_dtos = self.query_handler.get_all_customers()
        return [Customer.from_dto(dto) for dto in customer_dtos]

    @strawberry.field
    def search_customers(self, query: str) -> List[Customer]:
        """Search for customers by name."""
        customer_dtos = self.query_handler.search_customers_by_name(query)
        return [Customer.from_dto(dto) for dto in customer_dtos]