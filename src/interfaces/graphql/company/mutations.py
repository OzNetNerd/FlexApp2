"""
GraphQL mutation resolvers for the Company domain.

This module defines the mutation resolvers related to the Company domain
that will be available in the GraphQL API.
"""
import strawberry
from typing import Optional

from application.company.commands import (
    CreateCompanyCommand,
    UpdateCompanyCommand,
    DeleteCompanyCommand
)
from src.interfaces.graphql.company.types import Company, CompanyInput


@strawberry.type
class CompanyMutations:
    """
    GraphQL mutations for the Company domain.

    This class defines all Company-related mutations available in the GraphQL API.
    """

    @strawberry.mutation
    async def create_company(self, info, input: CompanyInput) -> Company:
        """
        Create a new company.

        Args:
            info: GraphQL resolver info containing the request context
            input: Company data for creation

        Returns:
            Company: The newly created company
        """
        command = CreateCompanyCommand(
            name=input.name,
            website=input.website,
            industry=input.industry
        )

        result = await info.context.unit_of_work.execute_command(command)
        return result

    @strawberry.mutation
    async def update_company(
            self,
            info,
            id: int,
            input: CompanyInput
    ) -> Optional[Company]:
        """
        Update an existing company.

        Args:
            info: GraphQL resolver info containing the request context
            id: ID of the company to update
            input: Updated company data

        Returns:
            Optional[Company]: The updated company or None if not found
        """
        command = UpdateCompanyCommand(
            company_id=id,
            name=input.name,
            website=input.website,
            industry=input.industry
        )

        result = await info.context.unit_of_work.execute_command(command)
        return result

    @strawberry.mutation
    async def delete_company(self, info, id: int) -> bool:
        """
        Delete a company.

        Args:
            info: GraphQL resolver info containing the request context
            id: ID of the company to delete

        Returns:
            bool: True if the company was successfully deleted, False otherwise
        """
        command = DeleteCompanyCommand(company_id=id)
        result = await info.context.unit_of_work.execute_command(command)
        return result