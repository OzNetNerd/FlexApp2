# src/interfaces/graphql/opportunity/mutations.py
"""GraphQL mutations for opportunity operations."""

import strawberry
from typing import Optional
from src.application.opportunity.commands import OpportunityCommandHandler
from src.application.opportunity.dto import CreateOpportunityDTO, UpdateOpportunityDTO
from src.interfaces.graphql.opportunity.types import Opportunity, CreateOpportunityInput, UpdateOpportunityInput


@strawberry.type
class OpportunityMutations:
    """GraphQL mutation resolvers for opportunity operations."""

    def __init__(self, command_handler: OpportunityCommandHandler):
        """Initialize with a command handler."""
        self.command_handler = command_handler

    @strawberry.mutation
    def create_opportunity(self, input: CreateOpportunityInput) -> Opportunity:
        """Create a new opportunity."""
        opportunity_dto = self.command_handler.create_opportunity(CreateOpportunityDTO(
            title=input.title,
            company_id=input.company_id,
            amount=input.amount,
            status=input.status,
            description=input.description,
            close_date=input.close_date
        ))
        return Opportunity.from_dto(opportunity_dto)

    @strawberry.mutation
    def update_opportunity(self, id: int, input: UpdateOpportunityInput) -> Optional[Opportunity]:
        """Update an existing opportunity."""
        opportunity_dto = self.command_handler.update_opportunity(id, UpdateOpportunityDTO(
            title=input.title,
            company_id=input.company_id,
            amount=input.amount,
            status=input.status,
            description=input.description,
            close_date=input.close_date
        ))
        if not opportunity_dto:
            return None
        return Opportunity.from_dto(opportunity_dto)

    @strawberry.mutation
    def delete_opportunity(self, id: int) -> bool:
        """Delete an opportunity."""
        return self.command_handler.delete_opportunity(id)