# src/interfaces/graphql/customer/mutations.py
"""GraphQL mutations for customer operations."""

import strawberry
from typing import Optional
from src.application.customer.commands import CustomerCommandHandler
from src.application.customer.dto import CreateCustomerDTO, UpdateCustomerDTO
from src.interfaces.graphql.customer.types import Customer, CreateCustomerInput, UpdateCustomerInput


@strawberry.type
class CustomerMutations:
    """GraphQL mutation resolvers for customer operations."""

    def __init__(self, command_handler: CustomerCommandHandler):
        """Initialize with a command handler."""
        self.command_handler = command_handler

    @strawberry.mutation
    def create_customer(self, input: CreateCustomerInput) -> Customer:
        """Create a new customer."""
        customer_dto = self.command_handler.create_customer(CreateCustomerDTO(
            name=input.name,
            email=input.email,
            phone=input.phone,
            company_id=input.company_id
        ))
        return Customer.from_dto(customer_dto)

    @strawberry.mutation
    def update_customer(self, id: int, input: UpdateCustomerInput) -> Optional[Customer]:
        """Update an existing customer."""
        customer_dto = self.command_handler.update_customer(id, UpdateCustomerDTO(
            name=input.name,
            email=input.email,
            phone=input.phone,
            company_id=input.company_id
        ))
        if not customer_dto:
            return None
        return Customer.from_dto(customer_dto)

    @strawberry.mutation
    def delete_customer(self, id: int) -> bool:
        """Delete a customer."""
        return self.command_handler.delete_customer(id)