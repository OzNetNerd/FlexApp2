# src/interfaces/graphql/opportunity/queries.py
"""GraphQL queries for opportunity operations."""

import strawberry
from typing import List, Optional
from src.application.opportunity.queries import OpportunityQueryHandler
from src.interfaces.graphql.opportunity.types import Opportunity


@strawberry.type
class OpportunityQueries:
    """GraphQL query resolvers for opportunity operations."""

    def __init__(self, query_handler: OpportunityQueryHandler):
        """Initialize with a query handler."""
        self.query_handler = query_handler

    @strawberry.field
    def opportunity(self, id: int) -> Optional[Opportunity]:
        """Get an opportunity by ID."""
        opportunity_dto = self.query_handler.get_opportunity_by_id(id)
        if not opportunity_dto:
            return None
        return Opportunity.from_dto(opportunity_dto)

    @strawberry.field
    def opportunities(self) -> List[Opportunity]:
        """Get all opportunities."""
        opportunity_dtos = self.query_handler.get_all_opportunities()
        return [Opportunity.from_dto(dto) for dto in opportunity_dtos]

    @strawberry.field
    def opportunities_by_company(self, company_id: int) -> List[Opportunity]:
        """Get opportunities for a specific company."""
        opportunity_dtos = self.query_handler.get_opportunities_by_company(company_id)
        return [Opportunity.from_dto(dto) for dto in opportunity_dtos]