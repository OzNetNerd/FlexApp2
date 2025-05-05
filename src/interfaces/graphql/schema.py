"""
GraphQL schema definition that combines all domain query and mutation types.

This module defines the root schema for the GraphQL API by composing
query and mutation types from different domain contexts.
"""
import strawberry
from typing import Any

# Import domain-specific query and mutation types
from src.interfaces.graphql.company.queries import CompanyQueries
from src.interfaces.graphql.company.mutations import CompanyMutations
from src.interfaces.graphql.customer.queries import CustomerQueries
from src.interfaces.graphql.customer.mutations import CustomerMutations
from src.interfaces.graphql.opportunity.queries import OpportunityQueries
from src.interfaces.graphql.opportunity.mutations import OpportunityMutations


@strawberry.type
class Query(CompanyQueries, CustomerQueries, OpportunityQueries):
    """
    Root GraphQL Query type that combines all domain-specific queries.

    This class inherits from all domain query classes to provide a unified
    GraphQL query interface across all domain contexts.
    """

    @strawberry.field
    def health_check(self) -> str:
        """
        Simple health check endpoint to verify GraphQL server is running.

        Returns:
            str: A simple "ok" status message
        """
        return "ok"


@strawberry.type
class Mutation(CompanyMutations, CustomerMutations, OpportunityMutations):
    """
    Root GraphQL Mutation type that combines all domain-specific mutations.

    This class inherits from all domain mutation classes to provide a unified
    GraphQL mutation interface across all domain contexts.
    """
    pass


# Create the schema instance used by the GraphQL server
schema = strawberry.Schema(query=Query, mutation=Mutation)