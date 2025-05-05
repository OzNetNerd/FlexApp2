"""
GraphQL query resolvers for the Company domain.

This module defines the query resolvers related to the Company domain
that will be available in the GraphQL API.
"""
import strawberry
from typing import List, Optional

from src.application.company.queries import (
    GetCompanyQuery,
    ListCompaniesQuery,
    GetCompanyDetailsQuery
)
from src.interfaces.graphql.company.types import Company, CompanyDetails


@strawberry.type
class CompanyQueries:
    """
    GraphQL queries for the Company domain.

    This class defines all Company-related queries available in the GraphQL API.
    """

    @strawberry.field
    async def company(self, info, id: int) -> Optional[Company]:
        """
        Get a company by ID.

        Args:
            info: GraphQL resolver info containing the request context
            id: The ID of the company to retrieve

        Returns:
            Optional[Company]: The requested company or None if not found
        """
        query = GetCompanyQuery(company_id=id)
        result = await info.context.unit_of_work.execute_query(query)
        return result if result else None

    @strawberry.field
    async def companies(
            self,
            info,
            limit: Optional[int] = 20,
            offset: Optional[int] = 0
    ) -> List[Company]:
        """
        Get a paginated list of companies.

        Args:
            info: GraphQL resolver info containing the request context
            limit: Maximum number of companies to return (default: 20)
            offset: Number of companies to skip (default: 0)

        Returns:
            List[Company]: Paginated list of companies
        """
        query = ListCompaniesQuery(limit=limit, offset=offset)
        return await info.context.unit_of_work.execute_query(query)

    @strawberry.field
    async def company_details(self, info, id: int) -> Optional[CompanyDetails]:
        """
        Get detailed information about a company.

        Args:
            info: GraphQL resolver info containing the request context
            id: The ID of the company to retrieve details for

        Returns:
            Optional[CompanyDetails]: Detailed company information or None if not found
        """
        query = GetCompanyDetailsQuery(company_id=id)
        result = await info.context.unit_of_work.execute_query(query)

        if not result:
            return None

        return CompanyDetails.from_dto(result)